import smtplib
import ssl
from email.message import EmailMessage


def tls_secure_email(
    mail_server: str,
    mail_port: int,
    email_from: str,
    email_to: str,
    auth_pass: str,
    content: str
) -> None:
    """
    Sends an email securely through an SMTP connection over TLS.

    Establishes a secure channel to the SMTP server using SSL/TLS, authenticates
    with the provided credentials, and sends the email message.

    Args:
        mail_server: SMTP server hostname or address
        mail_port: Port to connect to the SMTP server
        email_from: The email account sending the message
        email_to: The email address of the recipient
        auth_pass: The password for the sender's email account
        content: The body of the email to be sent

    Raises:
        smtplib.SMTPAuthenticationError: If the provided login credentials are invalid.
        ssl.SSLError: If SSL certificate verification fails.
        smtplib.SMTPException: If an SMTP-related error occurs after connection.

    Returns:
        None
    """
    # Create a secure SSL context
    context = ssl.create_default_context()

    # Create email message
    message = EmailMessage()
    message["From"] = email_from
    message["To"] = email_to
    message["Subject"] = "Secure Message"
    message.set_content(content)

    # Connect to the SMTP server over TLS
    with smtplib.SMTP(mail_server, mail_port) as server:
        # Start TLS encryption
        server.starttls(context=context)
        
        # Login with credentials
        server.login(email_from, auth_pass)
        
        # Send the email
        server.send_message(message)