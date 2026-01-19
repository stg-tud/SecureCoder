def handle_http_header(raw_data: bytes, valid_headers: list[bytes]) -> bytes:
    """
    Processes incoming raw network data to extract and validate an HTTP header.
    
    Args:
        raw_data: bytes, the raw incoming network data that contains or partially contains an HTTP header.
        valid_headers: list[bytes], a set of permissible HTTP header versions like [b"HTTP/1.1"] to ensure compatibility.
    
    Returns:
        bytes: the remaining part of the buffer after processing the valid HTTP header.
    
    Raises:
        ValueError: if the HTTP header is incomplete, invalid, or exceeds the maximum allowed size.
    
    Security Policy:
        The buffer holding the HTTP header is limited to 8192 bytes to prevent resource-exhaustion attacks.
    """
    MAX_HEADER_SIZE = 8192  # Enforce limit to prevent DoS via large headers

    if len(raw_data) > MAX_HEADER_SIZE:
        raise ValueError(f"HTTP header exceeds maximum size of {MAX_HEADER_SIZE} bytes")

    # Look for end of headers (double CRLF: \r\n\r\n)
    double_crlf = b"\r\n\r\n"
    header_end_index = raw_data.find(double_crlf)
    
    # If double CRLF is not found, the header is incomplete
    if header_end_index == -1:
        raise ValueError("Incomplete HTTP header: missing end-of-headers marker")

    # Extract the full header part (including the double CRLF)
    header_data = raw_data[:header_end_index + len(double_crlf)]

    # Parse the request line (first line of the header)
    first_crlf = raw_data.find(b"\r\n")
    if first_crlf == -1:
        raise ValueError("Invalid header: missing first CRLF")

    request_line = raw_data[:first_crlf]
    parts = request_line.split(b" ")
    
    if len(parts) < 2:
        raise ValueError("Invalid request line: too few parts")

    # Check HTTP version (last part of request line)
    http_version = parts[-1]
    
    if http_version not in valid_headers:
        raise ValueError(f"Unsupported HTTP version: {http_version.decode(errors='replace')}")

    # Validate method and path (basic format check)
    method = parts[0]
    target = parts[1]

    if not method or not target:
        raise ValueError("Invalid request line: missing method or target")

    # Optional: further validate method syntax (alphanumeric, common methods)
    if not method.isupper() or not method.isascii() or not method.isalpha():
        raise ValueError("Invalid HTTP method")

    # The remaining data after the full header
    remaining = raw_data[header_end_index + len(double_crlf):]

    return remaining