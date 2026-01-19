import smtplib
import ssl
from email.message import EmailMessage


def secure_smtp_send(smtp_server: str, port: int, sender_email: str, receiver_email: str, password: str, message: str) -> None:
    """
    Sends an email using SMTP over TLS.

    Args:
        smtp_server: The SMTP server address (e.g., 'smtp.gmail.com').
        port: The SMTP server port (e.g., 587 for TLS).
        sender_email: The sender's email address.
        receiver_email: The recipient's email address.
        password: The sender's email password.
        message: The email message content.

    Raises:
        smtplib.SMTPAuthenticationError: If the login credentials are incorrect.
        ssl.SSLError: If there's a problem with the SSL certificate.
        smtplib.SMTPException: For other SMTP-related issues.

    Returns:
        None. The function sends the email and closes the connection.
    """
    # Create a secure SSL context
    context = ssl.create_default_context()

    # Create an email message
    email_msg = EmailMessage()
    email_msg["From"] = sender_email
    email_msg["To"] = receiver_email
    email_msg["Subject"] = "Secure Message"
    email_msg.set_content(message)

    # Connect to the SMTP server and send the email
    with smtplib.SMTP(smtp_server, port) as server:
        # Start TLS encryption
        server.starttls(context=context)
        # Log in to the server
        server.login(sender_email, password)
        # Send the email
        server.send_message(email_msg)

# Unittests
