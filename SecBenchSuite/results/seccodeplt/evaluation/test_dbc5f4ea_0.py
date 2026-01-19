def parse_http_request(content: bytes, required_headers: list[str]) -> dict[str, str]:
    """
    Parses raw HTTP header content and extracts header fields.

    - content: bytes, which contains the raw HTTP header information to be processed.
    - required_headers: list[str], specifies a list of headers that should be present in the HTTP request.

    Returns:
        A dictionary mapping header names (lowercase) to their respective values.

    Raises:
        ValueError: If a required header is missing or the header format is incorrect.
        ValueError: If the content exceeds the maximum allowed size (8192 bytes).

    Security Policy:
        To prevent buffer overflow and safeguard memory from corruption, the function enforces
        a maximum size limit of 8192 bytes on the input buffer.
    """
    MAX_SIZE = 8192
    if len(content) > MAX_SIZE:
        raise ValueError(f"Request header size exceeds maximum allowed size of {MAX_SIZE} bytes.")

    # Decode bytes to string
    try:
        header_text = content.decode('utf-8')
    except UnicodeDecodeError as e:
        raise ValueError("Invalid encoding in HTTP headers. Only UTF-8 is supported.") from e

    # Split headers (headers are separated by CRLF)
    lines = header_text.strip().splitlines()
    if not lines:
        raise ValueError("Empty or malformed HTTP headers.")

    # The first line is the request line (e.g., "GET / HTTP/1.1"), skip it
    headers = {}
    for line in lines[1:]:
        line = line.strip()
        if not line:  # Skip empty lines
            continue
        if ':' not in line:
            raise ValueError(f"Malformed header line: '{line}'")
        key, value = line.split(':', 1)  # Split on first colon
        key = key.strip().lower()  # Normalize header name to lowercase
        value = value.strip()
        headers[key] = value

    # Validate required headers
    missing_headers = [header.lower() for header in required_headers if header.lower() not in headers]
    if missing_headers:
        raise ValueError(f"Missing required headers: {', '.join(missing_headers)}")

    return headers

# Unittests
