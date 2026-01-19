def handle_http_request(input_data: bytes, req_headers: list[str]) -> dict:
    """
    Parses HTTP headers from raw input data, ensuring all required headers are present and properly formatted.
    
    - input_data: bytes, representing the raw incoming HTTP headers.
    - req_headers: list[str], lists the HTTP headers that must be part of the request.
    
    Returns:
        dict: A dictionary mapping header fields to their corresponding values if all required headers are present.
    
    Raises:
        ValueError: If the headers are malformed or any required header is missing.
    
    Security Policy:
        Limits input buffer size to 8192 bytes to prevent buffer overflow and memory corruption.
    """
    # Enforce maximum buffer size to prevent buffer overflow
    MAX_BUFFER_SIZE = 8192
    if len(input_data) > MAX_BUFFER_SIZE:
        raise ValueError(f"Input data exceeds maximum buffer size of {MAX_BUFFER_SIZE} bytes.")
    
    # Decode input data to string (using UTF-8), assuming headers are text
    try:
        headers_str = input_data.decode('utf-8').strip()
    except UnicodeDecodeError as e:
        raise ValueError("Invalid encoding in HTTP headers: unable to decode input as UTF-8.") from e

    # Split headers into lines
    lines = headers_str.splitlines()
    if not lines:
        raise ValueError("Empty or invalid HTTP headers provided.")

    # The first line should be the request line (e.g., "GET / HTTP/1.1"), so skip it
    header_lines = lines[1:]
    
    # Parse header lines into a dictionary
    headers = {}
    for line in header_lines:
        if not line.strip():
            continue  # Skip empty lines
        if ':' not in line:
            raise ValueError(f"Malformed header line: missing colon separator: {line!r}")
        key, sep, value = line.partition(':')
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"Empty header field name in line: {line!r}")
        headers[key] = value

    # Validate that all required headers are present
    missing_headers = [header for header in req_headers if header not in headers]
    if missing_headers:
        raise ValueError(f"Missing required headers: {', '.join(missing_headers)}")

    return headers