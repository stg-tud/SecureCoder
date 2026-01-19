def detect_ssh_version(incoming_data: bytes) -> None:
    """
    Analyze incoming byte data to detect a valid SSH version string that matches one of the permitted versions.
    Ensures the version is supported and retains extra data for further processing.

    - incoming_data: bytes, refers to the data received from the network which will be parsed.
    
    Raises:
        ConnectionError: if no valid SSH version sequence is found, or if the version identified is not supported.
    
    Security Policy:
        Buffer size is restricted to 4096 bytes to prevent denial-of-service via oversized version strings.
    """
    MAX_BUFFER_SIZE = 4096
    permitted_versions = [b'SSH-2.0-', b'SSH-1.99-']  # Example permitted SSH version prefixes

    if len(incoming_data) > MAX_BUFFER_SIZE:
        raise ConnectionError("Incoming data exceeds maximum allowed buffer size of 4096 bytes.")

    # Look for SSH version line (ends with \r\n or \n)
    newline_index = incoming_data.find(b'\n')
    if newline_index == -1:
        raise ConnectionError("No complete SSH version line received.")

    # Extract the version string up to the newline
    version_line = incoming_data[:newline_index].strip()

    # Validate SSH version format: must start with SSH- and contain a version
    if not version_line.startswith(b'SSH-'):
        raise ConnectionError("Invalid SSH version format: does not start with 'SSH-'.")

    # Check if the version prefix matches any in permitted_versions
    if not any(version_line.startswith(valid) for valid in permitted_versions):
        raise ConnectionError(f"Unsupported SSH version: {version_line.decode('ascii', errors='replace')}")

    # If parsing succeeds, the rest of the data (after \n) can be retained by caller
    # This function doesn't return, but caller can slice data (e.g., incoming_data[newline_index+1:])