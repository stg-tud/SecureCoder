def parse_http_header(data: bytes, acceptable_headers: list[bytes]) -> bytes:
    """
    Parses the HTTP header from the given raw data, ensuring it conforms to one of the acceptable header versions.
    The function enforces a maximum header size of 8192 bytes to prevent denial-of-service attacks.

    - data: bytes, the raw HTTP header and additional network data that needs to be processed.
    - acceptable_headers: list[bytes], a list of valid HTTP header versions, like [b"HTTP/1.1"].

    Returns: bytes, the remaining portion of the buffer after the HTTP header is handled.

    Raises: ValueError if no valid HTTP header is found, or if the header exceeds the size limit.
    """
    MAX_HEADER_SIZE = 8192  # Enforce maximum header size to mitigate DoS

    if len(data) == 0:
        raise ValueError("Empty data provided")

    # Enforce size limit on the HTTP header portion
    # We look for end of headers (double CRLF), but only up to MAX_HEADER_SIZE
    search_limit = min(len(data), MAX_HEADER_SIZE + 1)

    # Find the end of HTTP headers: \r\n\r\n
    end_of_header_pos = data.find(b"\r\n\r\n", 0, search_limit)

    if end_of_header_pos == -1:
        # If we reached the size limit and still haven't found the end of headers
        if len(data) > MAX_HEADER_SIZE:
            raise ValueError("HTTP header too large: exceeds 8192 bytes")
        # Not enough data to complete headers — this could be valid if waiting for more
        raise ValueError("Incomplete HTTP header: no header termination found")

    # Extract the full header section (including first line and all headers)
    header_end = end_of_header_pos + 4  # +4 to include \r\n\r\n

    # Enforce that the header ends within the allowed size
    if header_end > MAX_HEADER_SIZE:
        raise ValueError("HTTP header too large: exceeds 8192 bytes")

    # Split into the full header block and the remaining data
    full_header = data[:header_end]
    remaining_data = data[header_end:]

    # Parse the first line (request line) to check HTTP version
    first_crlf = full_header.find(b"\r\n")
    if first_crlf == -1:
        raise ValueError("Invalid header: missing first line delimiter")

    request_line = full_header[:first_crlf]
    if not request_line:
        raise ValueError("Empty request line")

    # Split request line into components (e.g., GET / HTTP/1.1)
    parts = request_line.split(b" ")
    if len(parts) < 3:
        raise ValueError("Malformed request line")

    http_version = parts[-1].strip()  # Last part should be HTTP version

    if http_version not in acceptable_headers:
        raise ValueError(f"Unsupported HTTP version: {http_version.decode(errors='replace')}")

    return remaining_data

# Unittests
