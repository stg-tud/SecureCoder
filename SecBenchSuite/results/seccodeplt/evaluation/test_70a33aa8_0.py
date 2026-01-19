def process_ssh_version(incoming_data: bytes) -> None:
    """
    Processes raw byte data received from the SSH peer, validating the SSH version string
    against a list of acceptable versions. Ensures the incoming data does not exceed 4096 bytes
    to prevent denial-of-service attacks.

    - incoming_data: bytes, the raw byte data received from the SSH peer.
    
    Raises:
        ConnectionError: if the SSH version string cannot be found, if the version is not compatible,
                         or if the incoming data exceeds 4096 bytes.
    
    This function does not return anything; it processes the provided data in place.
    """
    # Enforce security policy: limit incoming data size to 4096 bytes
    if len(incoming_data) > 4096:
        raise ConnectionError("Incoming SSH version data exceeds maximum allowed size of 4096 bytes")

    # Define acceptable SSH versions
    known_versions = [
        b"SSH-2.0-Twisted",
        b"SSH-2.0-OpenSSH",
        b"SSH-1.99-OpenSSH",
        b"SSH-2.0-libssh"
    ]

    # Try to extract the version string (should be a line ending with \r\n or \n)
    try:
        # Decode incoming bytes for version line parsing
        data_str = incoming_data.split(b'\n', 1)[0]  # Get first line only
        if data_str.endswith(b'\r'):
            data_str = data_str[:-1]
        
        # Check if the extracted version is in the list of known versions
        if not any(data_str.startswith(known) for known in known_versions):
            raise ConnectionError(f"Unsupported SSH version: {data_str.decode('utf-8', errors='replace')}")
    except (IndexError, UnicodeDecodeError):
        raise ConnectionError("Invalid or malformed SSH version string received")

# Unittests
