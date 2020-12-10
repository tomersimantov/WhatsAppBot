from twilio.rest import Client
from bearer_token import TWILIO_TOKEN, TWILIO_SID

# auth
sid = TWILIO_SID
token = TWILIO_TOKEN
client = Client(sid, token)
contact_directory = {'tomer': '+972506324449'}

# sends a message through contact_directory list
def message(text):
    for key, value in contact_directory.items():
        client.messages.create(
            from_='whatsapp:+14155238886',
            body=text,
            to='whatsapp:' + value,
        )
