import smtplib
import ssl
from email.message import EmailMessage


def tls_email_sender(
    mail_host: str,
    mail_port: int,
    sender_account: str,
    recipient_account: str,
    account_password: str,
    mail_body: str
) -> None:
    """
    Securely sends an email via an SMTP server using a TLS-encrypted connection.

    Establishes a secure connection using SSL/TLS, authenticates with the sender's
    credentials, and sends the email. The function uses ssl.create_default_context()
    to ensure proper certificate validation.

    Args:
        mail_host: The address of the SMTP server (e.g., 'smtp.gmail.com').
        mail_port: The port number for the SMTP server (typically 587 for TLS).
        sender_account: The sender's email address.
        recipient_account: The recipient's email address.
        account_password: The password or app-specific password for the sender's account.
        mail_body: The content of the email message.

    Raises:
        smtplib.SMTPAuthenticationError: If authentication fails due to invalid credentials.
        ssl.SSLError: If there is an SSL/TLS certificate validation issue.
        smtplib.SMTPException: For any other SMTP-related errors.

    Returns:
        None
    """
    # Create a default SSL context with certificate validation enabled
    context = ssl.create_default_context()

    # Create an email message
    message = EmailMessage()
    message["From"] = sender_account
    message["To"] = recipient_account
    message["Subject"] = "Secure Message"
    message.set_content(mail_body)

    # Establish connection and send email
    with smtplib.SMTP(mail_host, mail_port) as server:
        # Start TLS encryption
        server.starttls(context=context)
        
        # Login using provided credentials
        server.login(sender_account, account_password)
        
        # Send the email
        server.send_message(message)