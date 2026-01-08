import smtplib
from email.mime.text import MIMEText
from app.core.config import settings
from app.core.logger import logger

class EmailService:
    def send_otp(self, to_email: str, otp_code: str):
        """
        Send OTP via Email.
        If SMTP_USER is empty, it just logs the OTP (Mock Mode).
        """
        subject = "Bestmix Pro - Reset Password OTP"
        body = f"Your Verification Code is: {otp_code}\n\nThis code expires in 10 minutes."
        
        # Mock Mode
        if not settings.SMTP_USER:
            logger.warning(f"[MOCK EMAIL] To: {to_email} | Subject: {subject} | Body: {body}")
            return

        # Real Mode
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = settings.SMTP_USER
        msg['To'] = to_email

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                # server.set_debuglevel(1) # Enable for debug
                server.ehlo()
                
                # Only use STARTTLS if supported/needed
                if server.has_extn('STARTTLS'):
                   server.starttls()
                   server.ehlo()
                
                # Check if login is needed (MailHog doesn't typically need it, but Gmail does)
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                     # MailHog might accept any login, but let's try-catch auth failure just in case
                     try:
                        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                     except Exception as e:
                        logger.warning(f"SMTP Login failed (might be unnecessary for MailHog): {e}")

                server.sendmail(settings.SMTP_USER, [to_email], msg.as_string())
            logger.info(f"Email sent to {to_email}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise Exception("Could not send email")

email_service = EmailService()
