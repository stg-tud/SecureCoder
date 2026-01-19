def handle_http_header(data: bytes, acceptable_headers: list[bytes]) -> bytes:
    """
    This function is part of a basic HTTP server that is responsible for handling incoming headers.
    It identifies whether a full header has been received and processes it. Any extra data that doesn't
    belong to the header is stored for later use.

    - data: bytes, network data that consists of the HTTP header and potentially other information.
    - acceptable_headers: list[bytes], an array of valid HTTP header versions, for instance ["HTTP/1.1"].
    
    Returns: bytes, the leftover portion of the buffer after the valid header is processed.
    
    Raises: ValueError if the header is missing, incomplete, or invalid.
    
    Security: The header buffer is capped at 8192 bytes to prevent large headers from causing server 
    slowdown or denial-of-service issues.
    """
    MAX_HEADER_SIZE = 8192  # Enforce maximum header size to prevent DoS

    if len(data) == 0:
        raise ValueError("Empty data received")

    # Enforce maximum header size
    if len(data) > MAX_HEADER_SIZE:
        raise ValueError("HTTP header exceeds maximum allowed size of 8192 bytes")

    # Look for the end of the HTTP header (double CRLF: \r\n\r\n)
    double_crlf = b"\r\n\r\n"
    header_end_index = data.find(double_crlf)

    if header_end_index == -1:
        raise ValueError("Incomplete HTTP header: missing end-of-headers marker")

    # Extract the full header (including the double CRLF)
    header_end_index += 4  # Include the \r\n\r\n in the header
    header = data[:header_end_index]

    # Validate that the header starts with a valid HTTP version
    header_line_end = header.find(b"\r\n")
    first_line = header[:header_line_end] if header_line_end != -1 else header.strip()

    if not any(first_line.startswith(accept_hdr) for accept_hdr in acceptable_headers):
        raise ValueError("Invalid or unsupported HTTP header version")

    # Return any data after the header (leftover buffer)
    leftover = data[header_end_index:]
    return leftover