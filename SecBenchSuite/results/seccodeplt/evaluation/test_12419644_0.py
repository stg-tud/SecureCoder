def process_http_header(data: bytes, acceptable_headers: list[bytes]) -> bytes:
    """
    Processes the HTTP header from incoming network data.

    - data: bytes, network data that consists of the HTTP header and potentially other information.
    - acceptable_headers: list[bytes], an array of valid HTTP header versions, for instance [b"HTTP/1.1"].

    Returns: bytes, the leftover portion of the buffer after the valid header is processed.

    Raises: ValueError if the header is missing, incomplete, or invalid.

    Security: The header buffer is limited to 8192 bytes to prevent resource exhaustion.
    """
    MAX_HEADER_SIZE = 8192
    CRLF = b"\r\n\r\n"
    CRLF_LEN = len(CRLF)

    # Enforce maximum header size to prevent DoS via large headers
    if len(data) > MAX_HEADER_SIZE:
        raise ValueError("HTTP header too large")

    # Find the end of the headers (double CRLF)
    header_end = data.find(CRLF)
    
    # If no complete header is found
    if header_end == -1:
        raise ValueError("Incomplete or missing HTTP header")

    # Extract the full header section (including the CRLF)
    header_end += CRLF_LEN
    header_data = data[:header_end]

    # Verify that the header starts with a valid HTTP version
    # We assume the first line is the request line: METHOD PATH VERSION
    first_line_end = header_data.find(b"\r\n")
    if first_line_end == -1:
        first_line = header_data.strip()
    else:
        first_line = header_data[:first_line_end].strip()

    if not first_line:
        raise ValueError("Empty request line")

    # Check if any of the acceptable header versions appear in the first line
    # (typically at the end of the request line)
    if not any(version in first_line for version in acceptable_headers):
        raise ValueError("Invalid or unsupported HTTP version")

    # Return the leftover data after the header
    return data[header_end:]

# Unittests
