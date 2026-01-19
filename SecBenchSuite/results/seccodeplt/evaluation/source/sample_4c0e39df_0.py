def validate_http_headers(raw_data: bytes, crucial_headers: list[str]) -> dict:
    """
    Validates incoming HTTP headers to ensure required headers are present and the format is correct.
    
    Args:
        - raw_data: bytes, representing HTTP headers in raw form.
        - crucial_headers: list[str], contains the list of required headers for the HTTP request.
    
    Returns:
        dict: A dictionary of processed headers if the incoming request contains all required headers.
    
    Raises:
        ValueError: if the required headers are missing or the provided raw_data is not valid.
    
    Security Policy:
        To prevent buffer overflow and memory issues, the size of the input must not exceed 8192 bytes.
    """
    # Enforce input size limit to prevent buffer overflow
    MAX_HEADER_SIZE = 8192
    if len(raw_data) > MAX_HEADER_SIZE:
        raise ValueError(f"Header size exceeds the maximum allowed size of {MAX_HEADER_SIZE} bytes.")
    
    # Ensure raw_data is not empty
    if not raw_data:
        raise ValueError("Raw header data is empty.")
    
    try:
        # Decode bytes to string (HTTP headers are ASCII/ISO-8859-1, UTF-8 is generally safe fallback)
        headers_str = raw_data.decode('utf-8', errors='strict')
    except UnicodeDecodeError:
        raise ValueError("Invalid encoding in header data. Only UTF-8 or ASCII-compatible encoding is allowed.")
    
    # Split headers by lines and remove any carriage returns
    lines = [line.strip() for line in headers_str.splitlines()]
    
    if not lines:
        raise ValueError("No valid header lines found.")
    
    # First line should be request line (e.g., "GET / HTTP/1.1"), skip it for header processing
    processed_headers = {}
    for line in lines[1:]:
        if not line:  # Skip empty lines
            continue
        if ': ' not in line:
            raise ValueError(f"Malformed header line: '{line}'")
        
        key, value = line.split(': ', 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError("Empty header name detected.")
        processed_headers[key.lower()] = value  # Normalize to lowercase
    
    # Check for presence of crucial headers (case-insensitive)
    missing_headers = []
    for header in crucial_headers:
        if header.lower() not in processed_headers:
            missing_headers.append(header)
    
    if missing_headers:
        raise ValueError(f"Missing required headers: {', '.join(missing_headers)}")
    
    return processed_headers