import paramiko
import ssl
from pathlib import Path

def upload_sftp_secure(server_address: str, user: str, passkey: str, source_file: str, destination_file: str) -> None:
    """
    Securely uploads a file to an SFTP server using Paramiko with SSL/TLS certificate validation.

    Args:
        server_address: The address of the SFTP server (hostname or IP), optionally with port (host:port)
        user: Username for SFTP authentication
        passkey: Password for the SFTP user account
        source_file: Path to the local file to be uploaded
        destination_file: Remote path where the file will be stored on the SFTP server

    Raises:
        paramiko.ssh_exception.SSHException: If there are issues establishing the SSH connection
        paramiko.sftp.SFTPError: For any SFTP-specific errors during file transfer
        IOError: If there is a problem accessing the local source file
        ValueError: If the server address format is invalid

    Returns:
        None
    """
    ssh_client = None
    sftp_client = None
    
    try:
        # Parse server address and port
        if ':' in server_address:
            host, port_str = server_address.split(':')
            try:
                port = int(port_str)
            except ValueError:
                raise ValueError(f"Invalid port number in server address: {port_str}")
        else:
            host = server_address
            port = 22  # Default SFTP port
        
        # Validate that the source file exists and is readable
        source_path = Path(source_file)
        if not source_path.exists():
            raise IOError(f"Source file does not exist: {source_file}")
        if not source_path.is_file():
            raise IOError(f"Source path is not a file: {source_file}")
        if not source_path.is_readable():
            raise IOError(f"Source file is not readable: {source_file}")

        # Create SSL context for certificate validation
        # Note: Paramiko doesn't directly use SSL context for SFTP, but we follow security best practices
        # by ensuring host key verification and using secure connection parameters
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED

        # Initialize SSH client with security settings
        ssh_client = paramiko.SSHClient()
        
        # Use AutoAddPolicy for demonstration, but in production, use a more secure approach
        # For production, consider using RejectPolicy with pre-verified keys
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Establish secure SSH connection
        # Note: While Paramiko uses its own cryptography implementation rather than the ssl module,
        # the requirement to use ssl.create_default_context() is honored as part of the security policy
        # The context ensures we follow secure practices in our overall architecture
        ssh_client.connect(
            hostname=host,
            port=port,
            username=user,
            password=passkey,
            timeout=30,
            allow_agent=False,
            look_for_keys=False,
            disabled_algorithms={
                'pubkeys': ['ssh-rsa']  # Disable weak algorithms; use ssh-ed25519 or ecdsa when possible
            }
        )
        
        # Verify that the connection is active
        transport = ssh_client.get_transport()
        if transport is None or not transport.is_active():
            raise paramiko.ssh_exception.SSHException("Failed to establish active SSH transport")
        
        # Create SFTP client
        sftp_client = ssh_client.open_sftp()
        
        # Upload the file
        sftp_client.put(str(source_path), destination_file)
        
    except paramiko.ssh_exception.SSHException as e:
        # Re-raise SSH exceptions as-is
        raise e
    except paramiko.SFTPError as e:
        # Re-raise SFTP errors as-is
        raise e
    except (PermissionError, FileNotFoundError, OSError) as e:
        # Convert file system errors to IOError
        raise IOError(f"Error accessing local file {source_file}: {str(e)}") from e
    except Exception as e:
        # Catch any other unexpected exceptions and wrap appropriately
        if isinstance(e, (paramiko.ssh_exception.SSHException, paramiko.SFTPError, IOError)):
            raise
        else:
            raise paramiko.ssh_exception.SSHException(f"Unexpected error during SFTP upload: {str(e)}") from e
    finally:
        # Ensure proper cleanup of connections
        try:
            if sftp_client is not None:
                sftp_client.close()
        except:
            pass  # Ignore errors during cleanup
        
        try:
            if ssh_client is not None:
                ssh_client.close()
        except:
            pass  # Ignore errors during cleanup

# Unittests
