import smtplib
import ssl
from email.message import EmailMessage


def email_via_tls(
    smtp_host: str,
    smtp_port: int,
    from_email: str,
    to_email: str,
    email_pass: str,
    msg_body: str
) -> None:
    """
    Sends an email via a TLS-encrypted SMTP connection.

    Args:
        smtp_host: The address of the SMTP server.
        smtp_port: The port number for the SMTP server (typically 587 for TLS).
        from_email: The sender's email address.
        to_email: The recipient's email address.
        email_pass: The password for the sender's email account.
        msg_body: The content of the email message.

    Raises:
        smtplib.SMTPAuthenticationError: If the credentials are invalid.
        ssl.SSLError: If there is an SSL certificate validation error.
        smtplib.SMTPException: For any other SMTP-related errors.

    Returns:
        None
    """
    # Create a secure SSL context with default settings (certificate validation enabled)
    context = ssl.create_default_context()

    # Create an email message
    message = EmailMessage()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = "Message from email_via_tls"
    message.set_content(msg_body)

    # Connect to the SMTP server and send the email
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        # Upgrade the connection to secure TLS mode
        server.starttls(context=context)
        
        # Login with provided credentials
        server.login(from_email, email_pass)
        
        # Send the email
        server.send_message(message)