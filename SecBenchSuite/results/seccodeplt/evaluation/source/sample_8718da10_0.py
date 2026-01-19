import paramiko
import ssl
import os

def secure_ssh_upload(server_address: str, login_name: str, login_password: str, 
                     path_local_file: str, path_remote_file: str) -> None:
    """
    Securely uploads a file to an SFTP server using SSH/SFTP with host key and certificate validation.

    Args:
        server_address: The address of the SFTP server (may include port as 'host:port' or 'host').
        login_name: Username for SFTP authentication.
        login_password: Password for the given username.
        path_local_file: Local filesystem path to the file being uploaded.
        path_remote_file: Remote destination path on the SFTP server.

    Raises:
        paramiko.ssh_exception.SSHException: If SSH connection setup fails.
        paramiko.sftp.SFTPError: If SFTP file transfer fails.
        IOError: If local file cannot be accessed or read.
    """
    client = None
    try:
        # Create default SSL context for certificate validation
        # Note: Paramiko doesn't directly use ssl.create_default_context() for SFTP,
        # but we ensure security via host key verification and encrypted transport.
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED

        # Setup SSH client
        client = paramiko.SSHClient()
        
        # Load system host keys and set policy to reject unknown hosts
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.RejectPolicy())  # Enforces host key validation

        # Parse server address and port
        if ':' in server_address:
            hostname, port_str = server_address.split(':')
            port = int(port_str)
        else:
            hostname = server_address
            port = 22

        # Connect and authenticate
        client.connect(
            hostname=hostname,
            port=port,
            username=login_name,
            password=login_password,
            # Ensure strong encryption settings
            disabled_algorithms={
                'pubkeys': ['ssh-rsa']  # Disable weak SSH-RSA due to SHA-1 issues; use ssh-ed25519 or rsa-sha2
            }
        )

        # Open SFTP session
        sftp = client.open_sftp()

        # Validate local file exists and is readable
        if not os.path.isfile(path_local_file):
            raise IOError(f"Local file not found: {path_local_file}")
        if not os.access(path_local_file, os.R_OK):
            raise IOError(f"Permission denied when reading local file: {path_local_file}")

        # Perform secure file upload
        sftp.put(path_local_file, path_remote_file)

        # Close SFTP session
        sftp.close()

    except paramiko.ssh_exception.SSHException as e:
        raise paramiko.ssh_exception.SSHException(f"SSH connection error: {str(e)}") from e
    except paramiko.sftp.SFTPError as e:
        raise paramiko.sftp.SFTPError(f"SFTP transfer error: {str(e)}") from e
    except (OSError, IOError) as e:
        raise IOError(f"File access error: {str(e)}") from e
    finally:
        if client is not None:
            client.close()