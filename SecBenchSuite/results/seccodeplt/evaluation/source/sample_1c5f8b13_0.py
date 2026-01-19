def parse_http_headers(header_data: bytes, mandatory_headers: list[str]) -> dict:
    """
    Parses and validates HTTP headers from raw byte data.

    - header_data: bytes, representing HTTP headers in raw form.
    - mandatory_headers: list[str], contains the list of required headers for the HTTP request.

    Returns:
        dict: A dictionary of processed headers (header name in lowercase -> value).

    Raises:
        ValueError: if header_data exceeds size limit, is malformed, or required headers are missing.
    """
    MAX_HEADER_SIZE = 8192  # Enforce input size limit to prevent buffer overflow

    if not isinstance(header_data, bytes):
        raise ValueError("Header data must be of type bytes.")
    
    if len(header_data) > MAX_HEADER_SIZE:
        raise ValueError(f"Header data exceeds the maximum allowed size of {MAX_HEADER_SIZE} bytes.")
    
    # Decode bytes to string (using ISO-8859-1 per HTTP spec for headers)
    try:
        headers_str = header_data.decode('iso-8859-1')
    except UnicodeDecodeError as e:
        raise ValueError("Header data contains invalid encoding.") from e

    # Split into lines and parse
    lines = headers_str.splitlines()
    if not lines:
        raise ValueError("Header data is empty.")

    # First line should be a request line (e.g., GET / HTTP/1.1), so skip it
    # Remaining lines should be headers
    headers = {}
    for line in lines[1:]:
        line = line.strip()
        if not line:  # Skip empty lines (end of headers)
            break
        if ':' not in line:
            raise ValueError(f"Invalid header format: missing colon in '{line}'")
        
        # Split only on first colon
        key, value = line.split(':', 1)
        key = key.strip().lower()  # Normalize header names to lowercase
        value = value.strip()
        headers[key] = value

    # Validate mandatory headers are present
    missing_headers = [hdr.lower() for hdr in mandatory_headers if hdr.lower() not in headers]
    if missing_headers:
        raise ValueError(f"Missing required headers: {', '.join(missing_headers)}")

    return headers