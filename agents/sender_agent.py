import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from memory.database import DatabaseManager

class SenderAgent:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.sender_email = ""
        self.app_password = ""
        self.memory = DatabaseManager()

    def send_email(self, lead_name, lead_email, pitch):
        subject = f"AI Strategy for {lead_name}"
        status = "Logged (Dry Run)" if self.dry_run else "Sent"
        
        if self.dry_run:
            self.memory.log_email(lead_name, lead_email, subject, pitch, status="Logged Successfully")
            return True

        # LIVE MODE
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = lead_email
            msg['Subject'] = subject
            msg['Bcc'] = self.sender_email
            msg.attach(MIMEText(pitch, 'plain'))

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.sender_email, self.app_password)
            server.send_message(msg)
            server.quit()
            
            self.memory.log_email(lead_name, lead_email, subject, pitch, status="Sent Successfully")
            return True
        except Exception as e:
            self.memory.log_email(lead_name, lead_email, subject, pitch, status=f"Failed: {str(e)}")
            return False
