from twilio.rest import Client
import configuration

config = configuration.load_configuration("twilio")

client = Client(config["account_sid"], config["auth_token"])

client.messages.create(from_="whatsapp:+14155238886", body="Attention: The forecast predicts rain and you have left the appartment without your umbrella", to=config["to_phone"])
