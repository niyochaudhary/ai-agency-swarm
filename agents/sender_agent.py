import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config
from memory.database import DatabaseManager


class SenderAgent:
    """
    Fast, reliable email sender using Gmail SMTP with:
    - Persistent SMTP connection (no reconnect per email)
    - Auto-reconnect on failure
    - Graceful skip of invalid emails
    - Rate limiting to stay within Gmail's 500/day limit
    """

    GMAIL_DAILY_LIMIT = 490   # Stay safely below 500/day

    def __init__(self, dry_run=None):
        self.dry_run = dry_run if dry_run is not None else (not config.LIVE_MODE)
        self.sender_email = config.SENDER_EMAIL
        self.app_password = config.EMAIL_PASSWORD
        self.memory = DatabaseManager()
        self._smtp_conn = None
        self._sent_today = 0
        # Pre-connect SMTP at startup so first email is instant
        if not self.dry_run:
            self._get_smtp_connection()

    # ── SMTP connection management ─────────────────────────────────────────

    def _get_smtp_connection(self):
        """Return a live SMTP connection; reconnect automatically if dead."""
        try:
            if self._smtp_conn:
                self._smtp_conn.noop()   # Ping to check if alive
                return self._smtp_conn
        except Exception:
            self._smtp_conn = None

        print("[Sender] 🔌 Connecting to Gmail SMTP...")
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.sender_email, self.app_password)
            self._smtp_conn = server
            print("[Sender] ✅ Gmail SMTP connected!")
        except smtplib.SMTPAuthenticationError:
            print(
                "[Sender] ❌ Gmail authentication FAILED!\n"
                "   ➤ Go to https://myaccount.google.com/apppasswords\n"
                "   ➤ Create an App Password (not your normal Gmail password)\n"
                "   ➤ Update EMAIL_PASSWORD in config.py with the App Password\n"
                "   ➤ Make sure 2-Step Verification is ON in your Google Account"
            )
            self._smtp_conn = None
        except Exception as e:
            print(f"[Sender] ❌ SMTP connection error: {e}")
            self._smtp_conn = None

        return self._smtp_conn

    def close_connection(self):
        """Gracefully close the persistent SMTP connection."""
        if self._smtp_conn:
            try:
                self._smtp_conn.quit()
            except Exception:
                pass
            self._smtp_conn = None

    # ── Validation ─────────────────────────────────────────────────────────

    def is_valid_email_format(self, email):
        """Local format check — no slow network calls."""
        if not email or not isinstance(email, str):
            return False
        parts = email.strip().split("@")
        return len(parts) == 2 and "." in parts[1] and len(parts[1]) > 2

    # ── Single email send ──────────────────────────────────────────────────

    def send_email(self, lead_name, lead_email, pitch):
        """Send one email. Returns True on success, False on any failure."""
        lead_email = (lead_email or "").strip()

        if not self.is_valid_email_format(lead_email):
            print(f"[SKIP] Invalid or missing email for '{lead_name}': '{lead_email}'")
            return False

        if self._sent_today >= self.GMAIL_DAILY_LIMIT:
            print(f"[LIMIT] Gmail daily limit ({self.GMAIL_DAILY_LIMIT}) reached. Stopping sends for today.")
            return False

        subject = f"AI Automation Strategy for {lead_name} — Exclusive Insight"

        if self.dry_run:
            print(f"[DRY RUN] Would send to {lead_email}")
            self.memory.log_email(lead_name, lead_email, subject, pitch, status="Dry Run")
            return True

        # Live send
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.sender_email
            msg["To"] = lead_email
            msg["Subject"] = subject
            msg.attach(MIMEText(pitch, "plain"))

            conn = self._get_smtp_connection()
            if not conn:
                print(f"[SKIP] No SMTP connection — cannot send to {lead_email}")
                return False

            conn.send_message(msg)
            self._sent_today += 1
            print(f"[Sender] ✅ Email sent → {lead_email}  (today: {self._sent_today}/{self.GMAIL_DAILY_LIMIT})")
            self.memory.log_email(lead_name, lead_email, subject, pitch, status="Sent Successfully")
            return True

        except smtplib.SMTPRecipientsRefused:
            print(f"[SKIP] Recipient refused (address likely doesn't exist): {lead_email}")
            self.memory.log_email(lead_name, lead_email, subject, pitch, status="Recipient Refused")
            self._smtp_conn = None
            return False

        except smtplib.SMTPSenderRefused:
            print("[ERROR] Gmail rejected our sender address. Check credentials in config.py.")
            self._smtp_conn = None
            return False

        except smtplib.SMTPDataError as e:
            print(f"[ERROR] Gmail data error (possibly daily limit hit): {e}")
            self._smtp_conn = None
            return False

        except Exception as e:
            print(f"[Sender] ❌ Send failed to {lead_email}: {e}. Will reconnect next attempt.")
            self._smtp_conn = None
            self.memory.log_email(lead_name, lead_email, subject, pitch, status=f"Failed: {str(e)}")
            return False

    # ── Bulk send ──────────────────────────────────────────────────────────

    def send_bulk(self, leads_list, delay_seconds=0.3):
        """
        Send emails to all leads in the list using a persistent SMTP connection.
        Rate: 1 email per second (safe for Gmail).
        leads_list: list of dicts → {name, email, pitch}
        """
        total = len(leads_list)
        sent = 0
        skipped = 0
        print(f"\n[Bulk Sender] 🚀 Starting: {total} emails @ 1 every {delay_seconds}s")

        for i, lead in enumerate(leads_list):
            if self._sent_today >= self.GMAIL_DAILY_LIMIT:
                print(f"[LIMIT] Daily Gmail limit reached at lead #{i+1}. Stopping.")
                break

            result = self.send_email(
                lead.get("name", ""),
                lead.get("email", ""),
                lead.get("pitch", "")
            )
            if result:
                sent += 1
            else:
                skipped += 1

            print(f"   Progress: {i+1}/{total} | ✅ Sent: {sent} | ⏭ Skipped: {skipped}")
            time.sleep(delay_seconds)

        self.close_connection()
        print(f"\n[Bulk Sender] ✅ Done! Sent: {sent} | Skipped: {skipped} | Total attempted: {total}")
        return sent
