from ftplib import FTP_TLS
import ssl

def ftp_tls_connection(host: str, username: str, password: str) -> None:
    """
    Establishes a secure FTP connection using FTP over TLS (FTPS), authenticates with the provided
    credentials, retrieves and prints a directory listing from the remote FTP server.

    :param host: The hostname or IP address of the FTP server.
    :param username: The username for the FTP server.
    :param password: The password for the FTP server.

    :return: None. The function retrieves and prints the directory listing from the server and closes the connection.

    :raises ftplib.error_perm: If the login credentials are incorrect.
    :raises ssl.SSLError: If there's a problem with the SSL certificate.
    :raises Exception: For other issues during connection.
    """
    context = ssl.create_default_context()  # Enforce secure SSL/TLS with certificate validation

    ftps = None
    try:
        # Connect to the FTP server using FTP over TLS
        ftps = FTP_TLS(context=context)
        ftps.connect(host)
        ftps.auth()  # Securely authenticate TLS channel
        ftps.login(user=username, passwd=password)

        # Request directory listing
        directory_listing = []
        ftps.retrlines('LIST', directory_listing.append)

        # Print each line of the directory listing
        for line in directory_listing:
            print(line)

    except Exception as e:
        raise e
    finally:
        if ftps:
            try:
                ftps.quit()  # Gracefully close the connection
            except Exception:
                ftps.close()  # Force close if quit fails

# Unittests
