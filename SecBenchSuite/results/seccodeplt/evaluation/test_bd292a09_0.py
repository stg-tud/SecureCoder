import smtplib
import ssl
from email.message import EmailMessage


def tls_secured_email(
    mail_server: str,
    smtp_port: int,
    send_address: str,
    receive_address: str,
    auth_password: str,
    mail_content: str
) -> None:
    """
    Sends an email via SMTP using a secured TLS connection.

    Args:
        mail_server: The address of the SMTP server.
        smtp_port: The port to use for SMTP (typically 587 for TLS).
        send_address: The sender's email address.
        receive_address: The recipient's email address.
        auth_password: The password for the sender's email account.
        mail_content: The content of the email to be sent.

    Raises:
        smtplib.SMTPAuthenticationError: If the provided credentials are invalid.
        ssl.SSLError: If there is an SSL certificate validation issue.
        smtplib.SMTPException: For any other SMTP-related errors.

    Returns:
        None
    """
    # Create a secure SSL context with certificate validation
    context = ssl.create_default_context()

    # Create an email message
    message = EmailMessage()
    message["From"] = send_address
    message["To"] = receive_address
    message["Subject"] = "Secure Email"
    message.set_content(mail_content)

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(mail_server, smtp_port)
        
        # Enable TLS encryption
        server.starttls(context=context)
        
        # Log in to the server
        server.login(send_address, auth_password)
        
        # Send the email
        server.send_message(message)
        
    except (smtplib.SMTPAuthenticationError, ssl.SSLError, smtplib.SMTPException):
        # Re-raise these specific exceptions as per requirements
        raise
    except Exception as e:
        # Convert any other exception to SMTPException for consistency
        raise smtplib.SMTPException(f"An unexpected error occurred: {e}") from e
    finally:
        try:
            server.quit()
        except:
            pass  # Ignore errors during disconnect

# Unittests
