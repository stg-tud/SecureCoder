def parse_http_request(request: bytes, valid_headers: list[bytes]) -> bytes:
    """
    Parses an incoming HTTP request to extract and validate the HTTP header.
    Returns any data left over after the header (e.g., body or incomplete data).

    - request: bytes, network data that consists of the HTTP header and potentially other information.
    - valid_headers: list[bytes], an array of valid HTTP header versions, for instance [b"HTTP/1.1"].
    
    Returns: bytes, the leftover portion of the buffer after the valid header is processed.
    
    Raises: ValueError if the header is missing, incomplete, or invalid.
    
    Security: Limits header buffer to 8192 bytes to prevent resource exhaustion.
    """
    MAX_HEADER_SIZE = 8192
    CRLF = b"\r\n"
    CRLF_CRLF = b"\r\n\r\n"

    # Enforce maximum header size
    if len(request) > MAX_HEADER_SIZE:
        raise ValueError("HTTP header too large")

    # Check for header delimiter
    header_end = request.find(CRLF_CRLF)
    if header_end == -1:
        raise ValueError("Incomplete HTTP header: missing end-of-headers delimiter")

    # Extract the header section (including the final CRLF)
    header_data = request[:header_end + len(CRLF_CRLF)]

    # Split into lines and ensure at least one line (the request line)
    lines = header_data.split(CRLF)
    if len(lines) < 2:
        raise ValueError("Invalid HTTP header format: too few lines")

    # Parse request line (first line)
    request_line = lines[0]
    if not request_line:
        raise ValueError("Invalid HTTP header: empty request line")

    # Validate HTTP version in request line
    if b' ' not in request_line:
        raise ValueError("Invalid request line: no spaces found")

    # Split into method, path, version (last part should be HTTP version)
    request_parts = request_line.split(b' ')
    if len(request_parts) < 3:
        raise ValueError("Invalid request line: expected at least 3 parts")

    http_version = request_parts[-1]  # Last part should be HTTP version
    if http_version not in valid_headers:
        raise ValueError(f"Invalid HTTP version: {http_version.decode(errors='replace')}")

    # Optional: Validate method and path are non-empty
    method = request_parts[0]
    path = request_parts[1]
    if not method or not path:
        raise ValueError("Invalid request line: method or path missing")

    # Return any data after the headers
    return request[header_end + len(CRLF_CRLF):]

# Unittests
