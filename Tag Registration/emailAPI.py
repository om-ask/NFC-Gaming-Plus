from simplegmail import Gmail


# params = {
#   "to": "mrasharabi@gmail.com",
#   "sender": "Contact@gaming.kfupm.org",
#   "subject": "My first email",
#   "msg_html": "<h1>Woah, my first email!</h1><br />This is an HTML email.",
#   "msg_plain": "Hi\n  How are you sensi omar?.",
#   "signature": True  # use my account signature
# }

class RepeatEmailer:

    def __init__(self, sender: str, subject: str, placeholder_msg_html: str):
        self.sender = sender
        self.subject = subject
        self.placeholder_msg_html = placeholder_msg_html

        # Open gmail auth
        self._gmail = Gmail()  # will open a browser window to ask you to log in and authenticate

    def send_repeat_email(self, to: str, *fill_placeholders: str):
        # Prepare message
        prepared_msg_html = self.placeholder_msg_html % fill_placeholders

        # Prepare email parameters
        params = {
            "to": to,
            "sender": self.sender,
            "subject": self.subject,
            "msg_html": prepared_msg_html,
            "signature": True  # use my account signature
        }

        # Send email
        return self._gmail.send_message(**params)
