def process_ssh_version(received_data: bytes, ssh_supported_versions: list[bytes]) -> None:
    """
    Parses received network data to extract the SSH version string, validates it against
    supported versions, and ensures buffer size limits are enforced to prevent DoS.

    :param received游戏代
    :param ssh_supported_versions: List of supported SSH version strings as bytes.
    :raises ConnectionError: If no valid SSH version is found or version is not supported.
    """
    # Enforce maximum buffer size to prevent DoS from oversized inputs
    MAX_BUFFER_SIZE = 4096
    if len(received_data) > MAX_BUFFER_SIZE:
        raise ConnectionError(f"Received data exceeds maximum allowed buffer size of {MAX_BUFFER_SIZE} bytes")

    # SSH protocol specification: version string ends with \r\n
    terminator = b"\r\n"
    end_index = received_data.find(terminator)

    if end_index == -1:
        raise ConnectionError("No SSH version string terminator found (\\r\\n)")

    # Extract the version line (must start at beginning of stream per SSH spec)
    version_string = received_data[:end_index]

    # Per SSH spec, version string must start with 'SSH-'
    if not version_string.startswith(b"SSH-"):
        raise ConnectionError("Invalid SSH version format: does not start with 'SSH-'")

    # Validate against supported versions
    if version_string not in ssh_supported_versions:
        raise ConnectionError(f"Unsupported SSH version: {version_string.decode('ascii', errors='replace')}")

    # If needed, remaining data after \r\n can be saved for后续 processing
    # (Not returned, but could be stored in a buffer elsewhere in a real implementation)

    # Function processes in place; no return value
    return