from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
import openai
import json
import smtplib
from email.mime.text import MIMEText

# Load config
with open("config.json") as f:
    config = json.load(f)

BUSINESS_NAME = config["business_name"]
SYSTEM_PROMPT = config["business_prompt"]

EMAIL_FROM = config["email_from"]
EMAIL_TO = config["email_to"]
SMTP_SERVER = config["smtp_server"]
SMTP_PORT = config["smtp_port"]
SMTP_USER = config["smtp_user"]
SMTP_PASS = config["smtp_pass"]

# Flask app
app = Flask(__name__)

# Set your OpenAI API Key
openai.api_key = "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"


@app.route("/voice", methods=["POST"])
def voice():
    """Answer incoming calls with AI"""
    resp = VoiceResponse()

    # Greet caller
    resp.say(
        f"Hello, thank you for calling {BUSINESS_NAME}. Please tell me how I can help.",
        voice="alice"
    )

    # Record their message
    resp.record(
        action="/process",
        max_length=15,
        transcribe=True,
        transcribe_callback="/process",
        play_beep=True
    )

    # If they don't say anything, leave a voicemail
    resp.say("If you need further assistance, please leave a message after the beep.")
    resp.record(action="/voicemail", max_length=30, play_beep=True)
    return str(resp)


@app.route("/process", methods=["POST"])
def process():
    """Handle transcription + AI reply"""
    transcription = request.form.get("TranscriptionText", "")
    print("Caller said:", transcription)

    # AI Response
    gpt_response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcription}
        ]
    )
    reply = gpt_response["choices"][0]["message"]["content"]

    print("AI says:", reply)

    # Twilio speaks the reply
    resp = VoiceResponse()
    resp.say(reply, voice="alice")
    resp.hangup()
    return str(resp)


@app.route("/voicemail", methods=["POST"])
def voicemail():
    """Handle voicemail recordings and send via email"""
    recording_url = request.form.get("RecordingUrl", "")
    caller = request.form.get("From", "Unknown Caller")

    print(f"Voicemail received from {caller}: {recording_url}")

    # Send email
    subject = f"Voicemail for {BUSINESS_NAME}"
    body = f"You have a new voicemail from {caller}.\n\nListen here: {recording_url}.mp3"

    send_email(subject, body)

    resp = VoiceResponse()
    resp.say("Thank you. Your message has been sent to the business. Goodbye!", voice="alice")
    resp.hangup()
    return str(resp)


def send_email(subject, body):
    """Send email with voicemail info"""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
            print("Voicemail email sent successfully")
    except Exception as e:
        print("Email sending failed:", e)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
