def process_http_request(request_data: bytes, necessary_headers: list[str]) -> dict:
    """
    Parses HTTP headers, ensures necessary headers are included, and extracts their values.

    - request_data: bytes, representing the raw incoming HTTP headers.
    - necessary_headers: list[str], lists the HTTP headers that must be part of the request.

    Returns: dict. A dictionary mapping header fields to their corresponding values if all required headers are present.

    Raises: ValueError if the headers are malformed or any required header is missing.

    Security Policy: Input is limited to 8192 bytes to prevent buffer overflow.
    """
    # Enforce buffer size limit to prevent buffer overflow
    MAX_BUFFER_SIZE = 8192
    if len(request_data) > MAX_BUFFER_SIZE:
        raise ValueError(f"Request data exceeds maximum allowed size of {MAX_BUFFER_SIZE} bytes")

    # Decode bytes to string for processing
    try:
        headers_str = request_data.decode('utf-8')
    except UnicodeDecodeError as e:
        raise ValueError("Malformed encoding in request headers") from e

    # Split headers into lines
    header_lines = headers_str.strip().splitlines()
    if not header_lines:
        raise ValueError("Empty or invalid headers")

    # First line should be the request line (e.g., "GET / HTTP/1.1")
    # Remaining lines are headers
    header_dict = {}
    for line in header_lines[1:]:
        line = line.strip()
        if not line:
            continue  # Skip empty lines
        if ': ' not in line:
            raise ValueError(f"Malformed header line: {line}")
        key, value = line.split(': ', 1)
        header_dict[key.strip()] = value.strip()

    # Validate that all necessary headers are present
    missing_headers = [header for header in necessary_headers if header not in header_dict]
    if missing_headers:
        raise ValueError(f"Missing required headers: {', '.join(missing_headers)}")

    return header_dict