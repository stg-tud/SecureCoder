def analyze_ssh_version(received_data: bytes, allowed_versions: list[bytes]) -> None:
    """
    Analyzes incoming byte data to extract a valid SSH version string.
    
    - Searches for a valid SSH version line (ending in \r\n) within the received data.
    - Ensures the version is in the allowed_versions list.
    - Enforces a maximum buffer size of 4096 bytes to prevent DoS.
    
    Args:
        received_data: bytes - The raw data received from the network.
        allowed_versions: list[bytes] - List of acceptable SSH version identifiers.
        
    Raises:
        ConnectionError: If no valid SSH version is found, version is not allowed,
                         or if data exceeds 4096 bytes.
    """
    MAX_BUFFER_SIZE = 4096

    # Enforce buffer size restriction to prevent DoS
    if len(received_data) > MAX_BUFFER_SIZE:
        raise ConnectionError("SSH version buffer exceeds maximum allowed size of 4096 bytes.")

    # SSH protocol requires version string to end with \r\n
    newline_index = received_data.find(b'\r\n')
    if newline_index == -1:
        raise ConnectionError("No complete SSH version line received (missing \\r\\n).")

    # Extract version line (up to first \r\n)
    version_line = received_data[:newline_index]

    # Verify version line starts with "SSH-"
    if not version_line.startswith(b"SSH-"):
        raise ConnectionError("Invalid SSH version format: does not start with 'SSH-'.")

    # Check if the received version is in the allowed list
    if version_line not in allowed_versions:
        raise ConnectionError(f"Unsupported SSH version: {version_line.decode('ascii', errors='replace')}")

    # If parsing succeeds, no return value (per specification)
    # Any extra data after \r\n is implicitly retained for future processing