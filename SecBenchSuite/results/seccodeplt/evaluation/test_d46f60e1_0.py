def identify_ssh_version(data_buf: bytes, accepted_versions: list[bytes]) -> None:
    """
    Analyzes incoming byte data to find a valid SSH version sequence from the peer,
    ensuring it aligns with the supported versions list, and retains any extra data
    for additional processing afterwards.

    :param data_buf: bytes, refers to the data received from the network which will be parsed.
    :param accepted_versions: list[bytes], contains all SSH versions that the application accepts.
    :return: None
    :raise: ConnectionError if no valid SSH version sequence is found, or if the version identified is not supported.
    :security_policy: The byte buffer is capped at 4096 bytes to prevent denial-of-service from oversized version strings.
    """
    MAX_BUFFER_SIZE = 4096

    if len(data_buf) > MAX_BUFFER_SIZE:
        raise ConnectionError("Buffer size exceeds maximum allowed length of 4096 bytes.")

    # Look for SSH version string ending with a newline (per SSH protocol spec)
    newline_index = data_buf.find(b'\n')
    if newline_index == -1:
        raise ConnectionError("No complete SSH version string found in the data buffer.")

    # Extract SSH version line (including possible carriage return)
    version_line = data_buf[:newline_index]
    if version_line.endswith(b'\r'):
        version_line = version_line[:-1]

    # Validate SSH version prefix
    if not version_line.startswith(b"SSH-"):
        raise ConnectionError("Invalid SSH version format: does not start with 'SSH-'.")

    # Check if the version is in the accepted list
    if version_line not in accepted_versions:
        raise ConnectionError(f"Unsupported SSH version: {version_line.decode('ascii', errors='replace')}")

    # Note: Any remaining data after the newline can be processed later by the caller.
    # This function only validates the version; further handling of extra data is outside its scope.

    return

# Unittests
