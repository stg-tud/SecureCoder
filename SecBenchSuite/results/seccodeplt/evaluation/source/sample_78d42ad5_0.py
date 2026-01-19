def handle_http_request(buffer: bytes, acceptable_headers: list[bytes]) -> bytes:
    """
    Processes the raw HTTP request buffer to extract and validate the HTTP header.
    Ensures the header size does not exceed 8192 bytes to prevent denial-of-service attacks.
    
    Args:
        - buffer: bytes, the raw HTTP header and additional network data that needs to be processed.
        - acceptable_headers: list[bytes], a list of valid HTTP header versions, like [b"HTTP/1.1"].

    Returns:
        bytes: the remaining portion of the buffer after the HTTP header is handled.

    Raises:
        ValueError: if no valid HTTP header is found, if the header exceeds 8192 bytes,
                    or if an error occurs during processing.
    """
    MAX_HEADER_SIZE = 8192  # Enforce limit to prevent DoS via oversized headers

    if len(buffer) == 0:
        raise ValueError("Empty buffer provided")

    # Limit header search to MAX_HEADER_SIZE to prevent excessive memory usage
    search_limit = min(len(buffer), MAX_HEADER_SIZE)
    header_end = buffer.find(b"\r\n\r\n", 0, search_limit)

    if header_end == -1:
        # No complete header found within size limit
        if len(buffer) >= MAX_HEADER_SIZE:
            raise ValueError("HTTP header exceeds maximum allowed size of 8192 bytes")
        raise ValueError("Incomplete HTTP header")

    # Extract the full header (including the double CRLF)
    header_end += 4  # Include the \r\n\r\n delimiter
    header_data = buffer[:header_end]

    # Parse the first line (request line) to validate HTTP version
    first_crlf = header_data.find(b"\r\n")
    if first_crlf == -1:
        raise ValueError("Malformed header: missing first line delimiter")

    request_line = header_data[:first_crlf]
    parts = request_line.split(b" ")
    if len(parts) < 3:
        raise ValueError("Invalid request line format")

    http_version = parts[2]  # Should be something like b"HTTP/1.1"

    if http_version not in acceptable_headers:
        raise ValueError(f"Unsupported HTTP version: {http_version.decode('latin1', errors='replace')}")

    # Return the remaining data after the header
    return buffer[header_end:]