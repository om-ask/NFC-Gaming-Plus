from simplegmail import Gmail


# params = {
#   "to": "mrasharabi@gmail.com",
#   "sender": "Contact@gaming.kfupm.org",
#   "subject": "My first email",
#   "msg_html": "<h1>Woah, my first email!</h1><br />This is an HTML email.",
#   "msg_plain": "Hi\n  How are you sensi omar?.",
#   "signature": True  # use my account signature
# }

def send_email(params):
    gmail = Gmail()  # will open a browser window to ask you to log in and authenticate
    message = gmail.send_message(**params)
