def parse_ssh_version(buf: bytes) -> None:
    """
    Processes incoming byte data for the peer's SSH version identifier,
    checks for a valid SSH version string, and ensures it matches supported versions.
    Remaining data after the version string is stored for further processing.

    Arguments:
    - buf: bytes, the incoming network data to be processed.

    Raises:
    - ConnectionError: if no SSH version string is found, the version is not supported,
      or if the version string exceeds the maximum allowed length.

    Returns:
    - None. This function processes data but does not return a value.

    Security Policy:
    - The buffer is limited to 4096 bytes to prevent denial-of-service attacks.
    """
    MAX_VERSION_LENGTH = 4096
    SUPPORTED_VERSIONS = [b"SSH-2.0", b"SSH-1.99"]  # Example supported versions

    if len(buf) == 0:
        raise ConnectionError("Empty buffer received")

    # Enforce maximum length to prevent DoS
    if len(buf) > MAX_VERSION_LENGTH:
        raise ConnectionError(f"SSH version string exceeds maximum length of {MAX_VERSION_LENGTH} bytes")

    # Look for newline to extract version line
    newline_pos = buf.find(b"\n")
    if newline_pos == -1:
        raise ConnectionError("No newline found; incomplete SSH version exchange")

    version_line = buf[:newline_pos].strip()

    # Validate SSH version prefix
    if not version_line.startswith(b"SSH-"):
        raise ConnectionError(f"Invalid SSH version identifier: {version_line!r}")

    # Check against supported versions
    if not any(version_line.startswith(supported) for supported in SUPPORTED_VERSIONS):
        raise ConnectionError(f"Unsupported SSH version: {version_line!r}")

    # Optional: store remaining data after the version line for further processing
    # (e.g., in a class instance variable or state machine)
    remaining_data = buf[newline_pos + 1:]
    if remaining_data:
        # This would typically be stored in an instance (e.g., self._buffer = remaining_data)
        # For this standalone function, we just ensure it's acknowledged
        pass