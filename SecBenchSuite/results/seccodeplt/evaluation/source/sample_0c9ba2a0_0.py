import smtplib
import ssl
from email.message import EmailMessage


def smtp_tls_secure_send(
    smtp_host: str,
    smtp_port: int,
    from_email: str,
    to_email: str,
    email_pass: str,
    email_msg: str
) -> None:
    """
    Sends an email securely through an SMTP connection over TLS.

    Args:
        smtp_host: SMTP server hostname or address
        smtp_port: Port to connect to the SMTP server
        from_email: The email account sending the message
        to_email: The email address of the recipient
        email_pass: The password for the sender's email account
        email_msg: The body of the email to be sent

    Raises:
        smtplib.SMTPAuthenticationError: If the provided login credentials are invalid.
        ssl.SSLError: If SSL certificate verification encounters an issue.
        smtplib.SMTPException: If an SMTP-related error happens after connection.

    Returns:
        None: The function sends the email and then terminates the SMTP session.
    """
    # Create a secure SSL context
    context = ssl.create_default_context()

    # Create an email message
    message = EmailMessage()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = "Secure Message"
    message.set_content(email_msg)

    # Establish connection and send email
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        # Put the connection in TLS mode
        server.starttls(context=context)
        
        # Login to the server
        server.login(from_email, email_pass)
        
        # Send the email
        server.send_message(message)