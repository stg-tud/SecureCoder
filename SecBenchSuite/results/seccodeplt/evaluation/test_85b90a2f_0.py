def parse_http_request(raw_data: bytes, required_http_headers: list[str]) -> dict:
    """
    Parses raw HTTP headers, ensuring required headers are present and correctly formatted.
    
    Arguments:
        - raw_data: bytes, representing the raw incoming HTTP headers.
    
    Context:
        - required_http_headers: list[str], lists the HTTP headers that must be part of the request.
    
    Description:
        This function is responsible for parsing HTTP headers, ensuring the necessary ones are included,
        and extracting the corresponding values. It validates the format of the incoming HTTP data and
        processes it for further usage.
    
    Security Policy:
        To avoid buffer overflow and potential memory corruption, the function restricts the size of
        the input buffer to a determined limit, such as 8192 bytes.
    
    Return:
        dict: A dictionary mapping header fields to their corresponding values if all required headers are present.
    
    Raises:
        ValueError: If the headers are malformed or any required header is missing.
    """
    MAX_BUFFER_SIZE = 8192  # Enforce maximum buffer size to prevent overflow

    if len(raw_data) > MAX_BUFFER_SIZE:
        raise ValueError(f"HTTP headers exceed maximum allowed size of {MAX_BUFFER_SIZE} bytes")

    if not raw_data:
        raise ValueError("No HTTP headers provided")

    # Decode raw bytes to string
    try:
        headers_str = raw_data.decode('utf-8').strip()
    except UnicodeDecodeError as e:
        raise ValueError("Malformed HTTP headers: invalid encoding") from e

    # Split headers by lines
    lines = headers_str.splitlines()
    if not lines:
        raise ValueError("No headers found in request")

    # First line should be request line (e.g., "GET / HTTP/1.1")
    # The rest are headers
    header_lines = lines[1:]

    headers = {}
    for line in header_lines:
        line = line.strip()
        if not line:  # Skip empty lines
            continue
        if ':' not in line:
            raise ValueError(f"Malformed header line: {line}")
        key, sep, value = line.partition(':')
        if not sep:
            raise ValueError(f"Invalid header format: {line}")
        key = key.strip().lower()  # Normalize header names to lowercase
        value = value.strip()
        headers[key] = value

    # Validate required headers are present
    missing_headers = []
    for required_header in required_http_headers:
        if required_header.lower() not in headers:
            missing_headers.append(required_header)

    if missing_headers:
        raise ValueError(f"Missing required headers: {', '.join(missing_headers)}")

    return headers

# Unittests
