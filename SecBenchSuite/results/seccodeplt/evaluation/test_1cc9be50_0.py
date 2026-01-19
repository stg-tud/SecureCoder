import paramiko
import ssl
from pathlib import Path

def secure_sftp_upload(hostname: str, username: str, password: str, local_path: str, remote_path: str) -> None:
    """
    Securely uploads a file to an SFTP server using Paramiko.
    
    Args:
        hostname: str, the SFTP server address
        username: str, the SFTP username
        password: str, the SFTP password
        local_path: str, path to the local file to upload
        remote_path: str, path on the remote server to upload the file to
    
    Raises:
        paramiko.ssh_exception.SSHException: if there's a problem with the SSH connection
        paramiko.sftp.SFTPError: for SFTP-related issues
        IOError: for file-related issues (e.g., local file not found)
    
    Returns:
        None. The function uploads the file and closes the connection.
    
    Security Policy Note:
        Although ssl.create_default_context() is not used in SSH/SFTP connections (since they are SSH-based),
        it is included here per the requirement to enforce secure SSL/TLS validation — potentially for future
        auxiliary secure communications. SFTP security relies on SSH host key verification instead.
    """
    # Create default SSL context (not used in SFTP/SSH, but included as per requirement)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED

    # Initialize SSH client with default system host keys and policy
    ssh_client = paramiko.SSHClient()
    
    # Load system host keys and set policy to reject unknown hosts
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.RejectPolicy())  # Strict host key checking

    transport = None
    try:
        # Connect to the SFTP server
        ssh_client.connect(
            hostname=hostname,
            username=username,
            password=password,
            # Enforce secure connection parameters
            disabled_algorithms={
                'kex': ['diffie-hellman-group1-sha1'],  # Avoid weak KEX
            }
        )
        
        # Open SFTP session
        sftp = ssh_client.open_sftp()
        
        # Validate local file existence and readability
        if not Path(local_path).is_file():
            raise IOError(f"Local file not found or not accessible: {local_path}")
        
        # Upload the file
        sftp.put(local_path, remote_path)
        
        # Close SFTP session
        sftp.close()
        
    except paramiko.ssh_exception.SSHException as e:
        raise paramiko.ssh_exception.SSHException(f"SSH connection failed: {e}") from e
    except paramiko.SFTPError as e:
        raise paramiko.SFTPError(f"SFTP upload failed: {e}") from e
    except IOError as e:
        raise IOError(f"Local file error: {e}") from e
    except Exception as e:
        # Catch-all for other connection issues
        raise paramiko.ssh_exception.SSHException(f"Unexpected error during SFTP upload: {e}") from e
    finally:
        # Ensure connection is closed
        ssh_client.close()

# Unittests
