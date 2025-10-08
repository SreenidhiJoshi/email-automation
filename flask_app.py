# flask_app.py
import os
from flask import Flask, request, jsonify
from send_email import send_emails_from_csv

app = Flask(__name__)

@app.route("/")
def health():
    return "OK", 200

@app.route("/send", methods=["POST"])
def send_endpoint():
    data = request.json or {}
    csv = data.get("csv", "recipients.csv")
    subject = data.get("subject", "Automated Mail")
    message = data.get("message", "Hello {name}, this is an automated email.")
    attachments = data.get("attachments", [])
    try:
        result = send_emails_from_csv(csv, subject, message, attachments=attachments)
        return jsonify({"status": "ok", "result": result}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
