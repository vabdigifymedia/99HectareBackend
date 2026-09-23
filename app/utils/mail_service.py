from pathlib import Path
import smtplib

from jinja2 import Environment, FileSystemLoader

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


# /var/task/app
APP_DIR = Path(__file__).resolve().parent.parent

# /var/task/app/templates
TEMPLATE_DIR = APP_DIR / "templates"

jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR)
)


class EmailService:

    @staticmethod
    async def send_template_email(
        to_email: str,
        subject: str,
        template_name: str,
        context: dict,
    ):
        template = jinja_env.get_template(template_name)

        html_content = template.render(
            subject=subject,
            **context,
        )

        message = MIMEMultipart("alternative")

        message["From"] = (
            f"{settings.SMTP_FROM_NAME} "
            f"<{settings.SMTP_FROM_EMAIL}>"
        )

        message["To"] = to_email
        message["Subject"] = subject

        message.attach(
            MIMEText(
                html_content,
                "html",
                "utf-8",
            )
        )

        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
        ) as server:

            server.ehlo()
            server.starttls()
            server.ehlo()

            server.login(
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD,
            )

            server.sendmail(
                settings.SMTP_FROM_EMAIL,
                to_email,
                message.as_string(),
            )
