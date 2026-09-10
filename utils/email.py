import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.config import settings


def send_order_confirmation_email(customer_email: str,customer_name: str,order_id: int,total_amount):

    subject = f"Order #{order_id} Confirmed"
    body = f"""
            Hello {customer_name},

            Your order has been confirmed successfully.

            Order ID: #{order_id}
            Total Amount: ₹{total_amount}

            Thank you for ordering with us.

            Regards,
            Food Delivery Team
            """

    message = MIMEMultipart()

    message["From"] = settings.SMTP_EMAIL
    message["To"] = customer_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(settings.SMTP_SERVER,settings.SMTP_PORT) as server:

        server.starttls()
        server.login(settings.SMTP_EMAIL,settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_EMAIL,customer_email,message.as_string())

def send_OTP_email(email: str,otp: str):

    subject = f"Otp for Your Mail varification"
    body = f"""
            Hello ,

            Yout Registration OTP is {otp} for {email} varification.DO not share this with others. this OTP valied upto 10 minitus
            Thank you for joining with us.

            Regards,
            Food Delivery Team
            """

    message = MIMEMultipart()

    message["From"] = settings.SMTP_EMAIL
    message["To"] = email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(settings.SMTP_SERVER,settings.SMTP_PORT) as server:

        server.starttls()
        server.login(settings.SMTP_EMAIL,settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_EMAIL,email,message.as_string())

def send_Success_update_password_email(email: str):

    subject = f"Congratulations"
    body = f"""
            Hello ,

            Your Password is Updated Successfull on {email}.
            Thank you for staying with us.

            Regards,
            Food Delivery Team
            """

    message = MIMEMultipart()

    message["From"] = settings.SMTP_EMAIL
    message["To"] = email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(settings.SMTP_SERVER,settings.SMTP_PORT) as server:

        server.starttls()
        server.login(settings.SMTP_EMAIL,settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_EMAIL,email,message.as_string())

def send_Success_registration_email(email: str, name:str):

    subject = f"Congratulations You rredistartion successfully"
    body = f"""
            Hello {name},

            Your registration with {email} has been done Successfull.
            Thank you for Joining with us.

            Regards,
            Food Delivery Team
            """

    message = MIMEMultipart()

    message["From"] = settings.SMTP_EMAIL
    message["To"] = email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(settings.SMTP_SERVER,settings.SMTP_PORT) as server:

        server.starttls()
        server.login(settings.SMTP_EMAIL,settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_EMAIL,email,message.as_string())
