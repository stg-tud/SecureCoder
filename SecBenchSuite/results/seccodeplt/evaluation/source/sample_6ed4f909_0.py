def validate_http_header(http_data: bytes) -> bytes:
    """
    Validates and processes an incoming HTTP header from raw network data.
    
    Args:
        http_data: bytes, the raw incoming network data that contains or partially contains an HTTP header.
    
    Returns:
        bytes: the remaining part of the buffer after processing the valid HTTP header.
    
    Raises:
        ValueError: if the HTTP header is incomplete, invalid, or exceeds the maximum allowed size.
    
    Security Policy:
        - The HTTP header (up to the double CRLF) must not exceed 8192 bytes to prevent resource exhaustion.
    """
    MAX_HEADER_SIZE = 8192
    valid_http_versions = [b"HTTP/1.1", b"HTTP/1.0"]  # Supported HTTP versions

    # Check if data exceeds maximum header size
    if len(http_data) > MAX_HEADER_SIZE:
        raise ValueError("HTTP header exceeds maximum allowed size of 8192 bytes")

    # Look for the end of the header (double CRLF: \r\n\r\n)
    header_end = http_data.find(b"\r\n\r\n")
    if header_end == -1:
        # Header is incomplete
        raise ValueError("Incomplete HTTP header: missing end delimiter \\r\\n\\r\\n")

    # Extract the full header block (including the final \r\n\r\n)
    header_block = http_data[:header_end + 4]

    # Enforce total header size limit (including the delimiter)
    if len(header_block) > MAX_HEADER_SIZE:
        raise ValueError("HTTP header exceeds maximum allowed size of 8192 bytes")

    # Split the header into lines
    header_lines = header_block.split(b"\r\n")
    if len(header_lines) < 1:
        raise ValueError("Empty HTTP header")

    # Parse the request line (first line)
    request_line = header_lines[0].strip()
    if not request_line:
        raise ValueError("Invalid request line: empty")

    # Request line format: METHOD SP URI SP VERSION
    parts = request_line.split(b" ")
    if len(parts) != 3:
        raise ValueError("Invalid HTTP request line format")

    method, uri, version = parts

    # Validate HTTP version
    if version not in valid_http_versions:
        raise ValueError(f"Unsupported HTTP version: {version.decode('utf-8', errors='replace')}")

    # Basic method and URI validation
    if not method.isupper() or not method.isalpha():
        raise ValueError("Invalid HTTP method")
    if len(uri) == 0 or uri[0] != 47 and not uri.startswith(b"http"):  # uri[0] != '/' unless absolute
        raise ValueError("Invalid URI")

    # If we've passed all checks, return the remaining data after the header
    return http_data[header_end + 4:]