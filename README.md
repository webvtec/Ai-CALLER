# AI Receptionist with Voicemail

This AI receptionist answers calls with GPT-4o and sends voicemails to the business owner via email.

## Features
- Greets callers and answers basic questions
- AI-driven responses using OpenAI
- Voicemail capture if unanswered
- Voicemails emailed automatically to the business owner

## Setup
1. Add your OpenAI API key in `app.py`
2. Update `config.json` with:
   - Business name
   - Prompt
   - Email settings
3. Deploy to Heroku/Render
4. In Twilio Console → Phone Number → Voice → A CALL COMES IN → set webhook URL to:
