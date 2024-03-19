import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

my_email = "gamererg@gmail.com"

def send_email(form_data):
    their_name = form_data["name"]
    their_email = form_data["email"]
    their_message = form_data["message"]

    subject = f"'Ten to None' Message: {their_name}"
    body = f"Name: {their_name}\nEmail: {their_email}\n\n{their_message}"

    # Create the MIME object
    message = MIMEMultipart()
    message["From"] = my_email
    message["To"] = my_email
    message["Subject"] = subject

    # Attach the body of the email
    message.attach(MIMEText(body, "plain"))

    # SMTP server configuration (for Gmail)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587  # Use 465 for SSL
    smtp_username = "gamererg@gmail.com"
    smtp_password = "czce mzhr thpl zdbx "

    # Establish a connection to the SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        # Start the TLS connection (for security)
        server.starttls()

        # Login to the email account
        server.login(smtp_username, smtp_password)

        # Send the email
        server.sendmail(my_email, "tentonone@proton.me", message.as_string())

# Testing the message
#message = {"name" : "John Doe", "email" : "johndoe@yahoo.com", "message" : "I like your website!"}
#send_email(message)