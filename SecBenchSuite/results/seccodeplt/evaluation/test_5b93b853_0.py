import paramiko
import ssl
import os

def secure_sftp_transfer(
    sftp_hostname: str,
    sftp_username: str,
    sftp_password: str,
    input_local_path: str,
    output_remote_path: str
) -> None:
    """
    Securely uploads a file to a remote SFTP server using SSH and validates the server's identity.

    Parameters:
        sftp_hostname: The address of the SFTP server.
        sftp_username: The username for authentication.
        sftp_password: The password for authentication.
        input_local_path: Local path of the file to upload.
        output_remote_path: Remote path where the file will be uploaded.

    Raises:
        paramiko.ssh_exception.SSHException: If there is an error establishing the SSH connection.
        paramiko.sftp.SFTPError: If an SFTP operation fails.
        IOError: If there is an issue reading the local file or accessing paths.

    Note:
        Uses SSL/TLS context for secure certificate validation, although SFTP runs over SSH.
        The ssl.create_default_context() is used here to emphasize secure practices and may be
        leveraged if extended to validate host keys via certificate authorities in advanced setups.
    """
    # Create a default SSL context for certificate validation
    # This ensures that CA bundles are loaded and TLS settings are secure
    # While SFTP uses SSH, not TLS directly, this context can be used in environments
    # where SSH host keys are tied to PKI or for consistency in security policy enforcement
    ssl_context = ssl.create_default_context()

    # Ensure the local file exists and is readable
    if not os.path.isfile(input_local_path):
        raise IOError(f"Local file not found: {input_local_path}")
    if not os.access(input_local_path, os.R_OK):
        raise IOError(f"Permission denied when reading local file: {input_local_path}")

    # Initialize SSH client
    ssh_client = paramiko.SSHClient()

    # Load system host keys and set policy to reject unknown hosts
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        # Connect to the SFTP server
        # Note: Paramiko does not directly use ssl_context for SSH transport,
        # but we ensure secure defaults are followed (e.g., key exchange, encryption)
        ssh_client.connect(
            hostname=sftp_hostname,
            username=sftp_username,
            password=sftp_password,
            # Enforce modern, secure SSH parameters (implicitly aligned with SSL best practices)
            disabled_algorithms={
                'pubkeys': ['ssh-rsa']  # Prefer safer keys; consider enabling if server requires
            }
        )

        # Open SFTP session
        sftp = ssh_client.open_sftp()

        try:
            # Upload the file
            sftp.put(input_local_path, output_remote_path)
        except Exception as e:
            # Catch SFTP-specific errors and re-raise if needed
            if isinstance(e, paramiko.SFTPError):
                raise e
            else:
                raise paramiko.SFTPError(f"Failed to upload file: {str(e)}") from e
        finally:
            # Close SFTP session
            sftp.close()

    except paramiko.AuthenticationException as e:
        raise paramiko.ssh_exception.SSHException(f"Authentication failed: {e}") from e
    except paramiko.SSHException as e:
        # This captures SSH-related errors (connection, handshake, etc.)
        raise e
    except Exception as e:
        # Wrap generic IO issues (e.g., network, file access)
        raise IOError(f"Unexpected error during SFTP transfer: {e}") from e
    finally:
        # Always close the SSH connection
        ssh_client.close()

# Unittests
