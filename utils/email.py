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