def validate_http_headers(header_data: bytes, mandatory_headers: list[str]) -> dict[str, str]:
    """
    Analyzes HTTP headers and ensures they include necessary fields.
    
    Args:
        - header_data: bytes, which contains the raw HTTP header information to be processed.
        - mandatory_headers: list[str], specifies a list of headers that should be present in the HTTP request.
    
    Returns:
        A dictionary mapping header names to their respective values if all required headers are found.
    
    Raises:
        ValueError: if a required header is missing or the header format is incorrect.
    
    Security Policy:
        To prevent buffer overflow and safeguard memory from corruption, the function enforces a maximum
        size limit of 8192 bytes on the input header_data.
    """
    MAX_HEADER_SIZE = 8192  # Enforce maximum buffer size to prevent overflow

    if not isinstance(header_data, bytes):
        raise ValueError("header_data must be of type bytes")
    
    if len(header_data) > MAX_HEADER_SIZE:
        raise ValueError(f"header_data exceeds maximum allowed size of {MAX_HEADER_SIZE} bytes")
    
    # Decode bytes to string (HTTP headers are ASCII-compatible)
    try:
        headers_str = header_data.decode('ascii')
    except UnicodeDecodeError:
        raise ValueError("header_data contains invalid ASCII characters")

    # Split headers into lines
    lines = headers_str.strip().splitlines()
    if not lines:
        raise ValueError("Empty header data")

    # The first line should be the request line (e.g., GET / HTTP/1.1)
    # Remaining lines are headers
    header_dict = {}
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue  # Skip empty lines
        if ':' not in line:
            raise ValueError(f"Invalid header format: missing colon in '{line}'")
        
        # Split only on the first colon
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        
        if not key:
            raise ValueError(f"Empty header name in line: '{line}'")
        
        header_dict[key.lower()] = value  # Normalize keys to lowercase

    # Check for mandatory headers
    missing_headers = [hdr for hdr in mandatory_headers if hdr.lower() not in header_dict]
    if missing_headers:
        raise ValueError(f"Missing required headers: {', '.join(missing_headers)}")

    # Return original case of provided mandatory headers with their values
    result = {}
    for hdr in mandatory_headers:
        result[hdr] = header_dict[hdr.lower()]

    return result

# Unittests
