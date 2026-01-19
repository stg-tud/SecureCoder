from typing import List

class ConnectionError(Exception):
    """Exception raised when an SSH connection error occurs."""
    pass


def extract_ssh_version(
    data: bytes,
    ssh_versions_supported: List[bytes]
) -> None:
    """
    Parses network data to extract the SSH version identifier from a peer,
    validates it against supported versions, and ensures buffer size limits
    are enforced to prevent denial-of-service attacks.

    Args:
        data: The byte data received from the network that needs to be parsed.
        ssh_versions_supported: A list of supported SSH version identifiers (as bytes).

    Raises:
        ConnectionError: If no SSH version string is found, if the version is not supported,
                         or if the data exceeds the maximum allowed buffer size.
    """
    MAX_BUFFER_SIZE = 4096

    # Enforce maximum buffer size to prevent DoS
    if len(data) > MAX_BUFFER_SIZE:
        raise ConnectionError(f"Received SSH version data exceeds maximum allowed size of {MAX_BUFFER_SIZE} bytes")

    # Look for a newline character to extract the version line
    newline_index = data.find(b'\n')
    if newline_index == -1:
        raise ConnectionError("No newline found; incomplete SSH version exchange")

    # Extract the version string (up to the first newline)
    version_line = data[:newline_index].strip()

    # Basic validation: must start with 'SSH-' 
    if not version_line.startswith(b'SSH-'):
        raise ConnectionError(f"Invalid SSH version format: {version_line.decode('ascii', errors='replace')}")

    # Validate against supported versions
    if version_line not in ssh_versions_supported:
        raise ConnectionError(f"Unsupported SSH version: {version_line.decode('ascii', errors='replace')}")

    # Note: Remaining unprocessed data (after newline) would typically be handled
    # by the caller or stored in a buffer; this function only parses and validates.