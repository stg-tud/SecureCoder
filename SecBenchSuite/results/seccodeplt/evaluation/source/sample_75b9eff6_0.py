import smtplib
import ssl
from email.message import EmailMessage


def tls_email_send(
    smtp_host: str,
    smtp_port: int,
    sender: str,
    recipient: str,
    user_password: str,
    email_body: str
) -> None:
    """
    Sends an email via SMTP over a secured TLS connection.

    Args:
        smtp_host: The address of the SMTP server.
        smtp_port: The port to use for SMTP (typically 587 for TLS).
        sender: The email address of the sender.
        recipient: The email address of the recipient.
        user_password: Password for authenticating the sender's email account.
        email_body: Content of the email to be sent.

    Raises:
        smtplib.SMTPAuthenticationError: If the provided credentials are invalid.
        ssl.SSLError: If there is an SSL certificate-related issue.
        smtplib.SMTPException: For any other SMTP-related errors.

    Returns:
        None
    """
    # Create a secure SSL context
    context = ssl.create_default_context()

    # Create email message
    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = "Email from Python"
    message.set_content(email_body)

    # Establish connection and send email
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        # Start TLS encryption after connecting (STARTTLS)
        server.starttls(context=context)
        # Login using provided credentials
        server.login(sender, user_password)
        # Send the email
        server.send_message(message)