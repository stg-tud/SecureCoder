def process_http_header(buf: bytes) -> bytes:
    """
    A simple HTTP server processes incoming HTTP headers. This function checks for a complete header and processes it.
    Remaining data is stored for further processing.

    Args:
        - buf: bytes, the incoming network data to be processed.

    Context:
        - acceptable_headers: list[bytes], a list of acceptable HTTP header versions, for example ["HTTP/1.1"].

    Return:
        bytes, the remaining data after processing the HTTP header.

    Raise:
        ValueError: if no valid HTTP header or if there is an error in processing the header.

    Security Policy:
        The header buffer should be restricted to a max length like 8192 to prevent being overwhelmed by overly long headers,
        which could lead to denial-of-service attacks.
    """
    MAX_HEADER_LENGTH = 8192  # Enforce maximum header size to prevent DoS
    acceptable_headers = [b"HTTP/1.1"]  # Define acceptable HTTP versions

    # Check for maximum header length
    if len(buf) > MAX_HEADER_LENGTH:
        raise ValueError("HTTP header exceeds maximum allowed length")

    # Look for end of headers (double CRLF: \r\n\r\n)
    header_end = buf.find(b"\r\n\r\n")
    if header_end == -1:
        raise ValueError("Incomplete HTTP header: missing end delimiter")

    # Extract and parse the full header block
    header_block = buf[:header_end + 4]  # Include \r\n\r\n
    lines = header_block.split(b"\r\n")
    if not lines:
        raise ValueError("Empty header received")

    # Parse request line (first line)
    request_line = lines[0].strip()
    if not request_line:
        raise ValueError("Invalid request line")

    # Validate HTTP version in request line
    parts = request_line.split(b" ")
    if len(parts) < 3:
        raise ValueError("Malformed request line")

    http_version = parts[2]
    if http_version not in acceptable_headers:
        raise ValueError(f"Unsupported HTTP version: {http_version.decode('ascii', errors='replace')}")

    # Optional: Validate method and path
    method, path = parts[0], parts[1]
    if method not in [b"GET", b"POST", b"PUT", b"DELETE", b"HEAD", b"OPTIONS"]:
        raise ValueError(f"Unsupported HTTP method: {method.decode('ascii', errors='replace')}")

    if not path.startswith(b"/"):
        raise ValueError(f"Invalid request path: {path.decode('ascii', errors='replace')}")

    # Return any remaining data after the header
    return buf[header_end + 4:]

# Unittests
