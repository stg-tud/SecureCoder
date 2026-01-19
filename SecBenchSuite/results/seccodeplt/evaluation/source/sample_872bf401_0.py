def handle_ssh_version(raw_data: bytes, supported_protocols: list[bytes]):
    """
    Parses network data to extract the SSH version identifier from a peer,
    validates it against a list of supported SSH versions, and saves any
    remaining unprocessed data for further operations.

    :param raw_data: bytes, the byte data received from the network that needs to be parsed.
    :param supported_protocols: list[bytes], a collection of SSH version identifiers that the application supports.
    :raises ConnectionError: when no SSH version string can be identified, or when the identified version isn't supported.
    :security_policy: To prevent excessive resource consumption, limit the buffer to a maximum length of 4096 bytes,
                      ensuring no denial-of-service attempt is made using overly large version strings.
    """
    if not raw_data:
        raise ConnectionError("No data received from peer.")

    # Enforce maximum buffer size to prevent DoS via large payloads
    if len(raw_data) > 4096:
        raise ConnectionError("SSH version string exceeds maximum allowed length of 4096 bytes.")

    # Look for the SSH version string, which should be the first line ending in \n or \r\n
    newline_index = raw_data.find(b'\n')
    if newline_index == -1:
        raise ConnectionError("SSH version string must be terminated with a newline character.")

    version_line = raw_data[:newline_index].strip()

    # Basic validation: must start with 'SSH-'
    if not version_line.startswith(b"SSH-"):
        raise ConnectionError("Invalid SSH version identifier: does not start with 'SSH-'.")

    # Validate the version against supported protocols
    if version_line not in supported_protocols:
        raise ConnectionError(f"Unsupported SSH version: {version_line.decode('ascii', errors='replace')}")

    # If needed, the remaining data after the newline can be processed or saved by higher-level logic
    # For now, this function just validates and enforces policy