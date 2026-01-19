def verify_http_header(header_data: bytes, acceptable_headers: list[bytes]) -> bytes:
    """
    Verifies that the provided data starts with a valid HTTP header line and processes the header.
    Enforces a maximum header size of 8192 bytes to prevent denial-of-service attacks.
    Returns any data that comes after the HTTP headers (e.g., body or leftover buffer).

    :param header_data: bytes, the raw HTTP header and additional network data.
    :param acceptable_headers: list[bytes], valid HTTP header versions (e.g., [b"HTTP/1.1"]).
    :return: bytes, the remaining portion of the buffer after the HTTP header.
    :raises: ValueError if no valid HTTP header is found or processing fails.
    """
    MAX_HEADER_SIZE = 8192  # Enforce limit to prevent DoS via large headers

    if len(header_data) == 0:
        raise ValueError("Empty header data provided")

    # Enforce size limit
    if len(header_data) > MAX_HEADER_SIZE:
        raise ValueError(f"HTTP header exceeds maximum allowed size of {MAX_HEADER_SIZE} bytes")

    # Find the end of the headers (double CRLF: \r\n\r\n)
    double_crlf = header_data.find(b"\r\n\r\n")
    if double_crlf == -1:
        raise ValueError("Incomplete HTTP header: missing end-of-headers marker")

    # Extract the header section (up to and including \r\n\r\n)
    header_section = header_data[:double_crlf + 4]

    # Split the header into lines and decode the request line
    header_lines = header_section.split(b"\r\n")
    if len(header_lines) == 0:
        raise ValueError("No header lines found")

    # The first line is the request line (e.g., "GET / HTTP/1.1")
    request_line = header_lines[0].strip()

    # Validate that the request line contains at least three parts: METHOD PATH VERSION
    parts = request_line.split()
    if len(parts) != 3:
        raise ValueError("Invalid HTTP request line format")

    method, path, version = parts

    # Validate the HTTP version is in the acceptable list
    if version not in acceptable_headers:
        raise ValueError(f"Unsupported HTTP version: {version.decode('utf-8', errors='replace')}")

    # Optional: Basic validation of method and path (non-empty)
    if not method or not path:
        raise ValueError("Invalid HTTP method or path")

    # Return any data after the headers (e.g., body or leftover buffer)
    return header_data[double_crlf + 4:]

# Unittests
