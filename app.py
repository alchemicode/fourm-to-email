from flask import Flask, request
from flask_cors import CORS
from envelopes import Envelope
from discord_webhook import DiscordWebhook
import toml, os, sys

if not os.path.exists("settings.toml"):
    print(
        "No config file found. Perhaps you need to rename 'ex_settings.toml' and edit it?"
    )
    sys.exit(1)

settings = toml.loads(open("settings.toml").read())

email_settings = settings["email"]
print(email_settings)

discord_settings = settings["discord"]
print(discord_settings)


app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        name = request.json["name"]
        email = request.json["email"]
        msg = request.json["message"]
        print(name + "<" + email + "> said: " + msg)

        if email_settings["enabled"]:
            for to_addr in email_settings["to"]:
                envelope = Envelope(
                    from_addr=(email_settings["from"], email_settings["my_name"]),
                    to_addr=(to_addr, "Recipient"),
                    subject="Form submission by " + name,
                    text_body="From '" + email + "': \n'" + msg + "'\n- " + name,
                )

                envelope.send(
                    email_settings["server"],
                    login=email_settings["from"],
                    password=email_settings["password"],
                    tls=email_settings["tls"],
                )

                print("Sent a copy to " + to_addr)

        if discord_settings["enabled"]:
            webhook = DiscordWebhook(
                url=discord_settings["url"],
                content="From `" + email + "`: \n`" + msg + "`\n- `" + name + "`",
            )
            webhook.execute()
            print("Sent a copy to discord webhook")

        return "Handled."
    else:
        return "Error."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090, debug=True)
