import smtplib
import ssl
from email.message import EmailMessage


def smtp_tls_mail_send(
    mail_host: str,
    server_port: int,
    user_email: str,
    recipient_id: str,
    login_password: str,
    mail_text: str
) -> None:
    """
    Sends an email via SMTP over a secured TLS connection.

    Args:
        mail_host: The address of the SMTP server.
        server_port: The port to use for SMTP (typically 587 for TLS).
        user_email: The sender's email address.
        recipient_id: The recipient's email address.
        login_password: The password for the sender's email account.
        mail_text: The content of the email.

    Raises:
        smtplib.SMTPAuthenticationError: If the provided credentials are invalid.
        ssl.SSLError: If there is an issue with SSL certificate validation.
        smtplib.SMTPException: For any other SMTP-related errors.

    Returns:
        None
    """
    # Create a secure SSL context
    context = ssl.create_default_context()

    # Create email message
    message = EmailMessage()
    message["From"] = user_email
    message["To"] = recipient_id
    message["Subject"] = "Notification"
    message.set_content(mail_text)

    # Establish connection and send email
    with smtplib.SMTP(mail_host, server_port) as server:
        # Start TLS encryption
        server.starttls(context=context)
        
        # Login using provided credentials
        server.login(user_email, login_password)
        
        # Send the email
        server.send_message(message)