import smtplib
import ssl
from email.message import EmailMessage


def secure_tls_email(
    smtp_host: str,
    smtp_port: int,
    mail_from: str,
    mail_to: str,
    mail_password: str,
    mail_content: str
) -> None:
    """
    Sends an email securely through an SMTP connection over TLS.

    Args:
        smtp_host: SMTP server hostname or address.
        smtp_port: Port to connect to the SMTP server (typically 587 for TLS).
        mail_from: The sender's email address.
        mail_to: The recipient's email address.
        mail_password: The sender's email account password.
        mail_content: The body of the email to be sent.

    Raises:
        smtplib.SMTPAuthenticationError: If the provided login credentials are invalid.
        ssl.SSLError: If SSL certificate verification fails.
        smtplib.SMTPException: If an SMTP-related error occurs after connection.

    Returns:
        None
    """
    # Create a secure SSL context with default settings for certificate verification
    context = ssl.create_default_context()

    # Create an email message
    message = EmailMessage()
    message["From"] = mail_from
    message["To"] = mail_to
    message["Subject"] = "Secure Message"
    message.set_content(mail_content)

    # Establish connection and send email
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        # Put the connection in TLS mode
        server.starttls(context=context)
        
        # Login using provided credentials
        server.login(mail_from, mail_password)
        
        # Send the email
        server.send_message(message)