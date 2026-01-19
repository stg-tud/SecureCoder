import smtplib
import ssl
from email.message import EmailMessage


def send_secure_email(
    mail_server: str,
    server_port: int,
    from_address: str,
    to_address: str,
    user_password: str,
    email_content: str
) -> None:
    """
    Sends an email securely using SMTP with TLS encryption.

    Establishes a secure connection to the SMTP server using TLS, authenticates
    with the provided credentials, and sends the email. The function ensures
    server certificate validation via ssl.create_default_context().

    Args:
        mail_server: The address of the SMTP server (e.g., 'smtp.gmail.com').
        server_port: The port number for the SMTP server (typically 587 for TLS).
        from_address: The sender's email address.
        to_address: The recipient's email address.
        user_password: The sender's email account password or app-specific password.
        email_content: The content of the email message.

    Raises:
        smtplib.SMTPAuthenticationError: If the credentials are invalid.
        ssl.SSLError: If there is an SSL/TLS certificate validation issue.
        smtplib.SMTPException: For any other SMTP-related error.
    """
    # Create a secure SSL context with default settings and certificate validation
    context = ssl.create_default_context()

    # Create an email message
    message = EmailMessage()
    message["From"] = from_address
    message["To"] = to_address
    message["Subject"] = "Secure Message"
    message.set_content(email_content)

    # Establish connection to the SMTP server
    try:
        with smtplib.SMTP(mail_server, server_port) as server:
            # Start TLS encryption
            server.starttls(context=context)
            
            # Login using provided credentials
            server.login(from_address, user_password)
            
            # Send the email
            server.send_message(message)
            
    except (smtplib.SMTPAuthenticationError, ssl.SSLError, smtplib.SMTPException):
        # Re-raise specific exceptions as per the policy
        raise
    except Exception as e:
        # Convert any other SMTP-related exception
        raise smtplib.SMTPException(f"Failed to send email: {str(e)}") from e

# Unittests
