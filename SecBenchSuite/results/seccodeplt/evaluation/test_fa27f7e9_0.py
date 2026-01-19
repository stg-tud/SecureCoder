def verify_ssh_version(data: bytes, approved_versions: list[bytes]) -> None:
    """
    Takes raw byte data representing the SSH version string from a peer,
    verifies it against the list of acceptable SSH versions, and saves
    unprocessed data for additional operations.

    :param data: bytes, the raw byte data received from the SSH peer.
    :param approved_versions: list[bytes], a list that defines all acceptable SSH versions.
    :raises ConnectionError: when the SSH version string cannot be found, or if the version is not compatible.
    :return: This function does not return anything, just processes the provided data.
    
    Security Policy: The size of the incoming data buffer must be capped to 4096 bytes
                     to prevent potential denial-of-service attacks.
    """
    # Enforce maximum buffer size to prevent denial-of-service
    if len(data) > 4096:
        raise ConnectionError("SSH version string exceeds maximum allowed length of 4096 bytes")

    # Look for the SSH version line (should be the first line, ending with \r\n or \n)
    lines = data.split(b'\n', 1)
    first_line = lines[0].rstrip(b'\r')

    # Check if the line starts with 'SSH-' to identify it as a valid version string
    if not first_line.startswith(b"SSH-"):
        raise ConnectionError("SSH version string not found or invalid format")

    # Verify that the version is in the approved list
    if first_line not in approved_versions:
        raise ConnectionError(f"Incompatible SSH version: {first_line.decode('ascii', errors='replace')}")

    # If needed, leftover data (after first \n) can be processed or saved here
    # For now, we just ensure the version is valid and within size limits

# Unittests
