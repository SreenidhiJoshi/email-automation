# send_email.py
import os
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_emails_from_csv(csv_path, subject, message_template, attachments=None):
    """
    Send emails listed in csv_path.
    csv must have columns: name,email,message (message optional; if present used instead of template)
    """
    sender_email = os.getenv("EMAIL_ADDRESS")
    app_password = os.getenv("APP_PASSWORD")

    if not sender_email or not app_password:
        raise RuntimeError("EMAIL_ADDRESS and APP_PASSWORD must be set as environment variables")

    data = pd.read_csv(csv_path)
    data.columns = data.columns.str.strip()

    if 'email' not in data.columns or 'name' not in data.columns:
        raise RuntimeError("CSV must contain 'name' and 'email' columns")

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, app_password)

    success = 0
    failures = []

    for _, row in data.iterrows():
        to_email = row['email']
        name = row['name']
        # pick message: per-row message overrides template if present
        if 'message' in data.columns and isinstance(row.get('message'), str) and row['message'].strip():
            body_text = row['message']
        else:
            body_text = message_template.replace("{name}", name)

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body_text, 'plain'))

        # attachments list of file paths
        if attachments:
            from email.mime.base import MIMEBase
            from email import encoders
            for fpath in attachments:
                try:
                    with open(fpath, 'rb') as f:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(fpath)}"')
                    msg.attach(part)
                except Exception as e:
                    # log but continue
                    print(f"Failed to attach {fpath}: {e}")

        try:
            server.sendmail(sender_email, to_email, msg.as_string())
            print(f"Sent to {name} <{to_email}>")
            success += 1
        except Exception as e:
            print(f"Failed to send to {to_email}: {e}")
            failures.append((to_email, str(e)))

    server.quit()
    return {"success": success, "failures": failures}

# CLI usage
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Send emails from CSV")
    parser.add_argument("--csv", default="recipients.csv", help="Path to recipients CSV")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--message", required=True, help="Message template (use {name} to personalize)")
    parser.add_argument("--attach", nargs="*", default=[], help="Files to attach")
    args = parser.parse_args()
    result = send_emails_from_csv(args.csv, args.subject, args.message, attachments=args.attach)
    print(result)
