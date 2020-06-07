import smtplib
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import fbchat
# import telegram as telegram
from fbchat import ThreadType


def retry_logging(func):
    def wrapper(*args, **kwargs):
        pass

    pass


class Notifier(ABC):
    """
    Each distinct product of a product family should have a base interface. All
    variants of the product must implement this interface.
    """

    @abstractmethod
    def log_into(self, login, password) -> int:
        pass

    @abstractmethod
    def message_myself(self, content,web) -> int:
        pass


class fb_chat(Notifier):
    client: fbchat.Client

    def log_into(self, login, password):
        try:
            self.client = fbchat.Client("notifaay@gmail.com", "TestTest123")
        except:
            return 0
        return 1

    def message_myself(self, content,web):
        content= "CHANGE DETECTED ON"+Website+"\n "+content
        sent = self.client.sendMessage(content, thread_id=self.client.uid, thread_type=ThreadType.USER)
        if sent:
            return 1
        else:
            return 0


class telegram_chat(Notifier):
    # bot = telegram.Bot('TOKEN')

    def log_into(self, login, password):
        pass

    def message_myself(self, content,web):
        pass


class discord_chat(Notifier):
    def log_into(self, login, password):
        pass

    def message_myself(self, content,web):
        pass


class mail_chat(Notifier):
    smtpserver: smtplib.SMTP
    mail: str

    def log_into(self, login, password):
        self.smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
        self.smtpserver.ehlo()
        self.smtpserver.starttls()
        self.smtpserver.ehlo()
        self.smtpserver.login("notifaay@gmail.com", "TestTest123")
        self.mail = login

    def message_myself(self, content,web):
        msg = MIMEMultipart()
        msg['From']="notifaay@gmail.com"
        msg['TO']=self.mail

        msg['Subject'] = "CHANGE DETECTED ON "+web
        msg.attach(MIMEText(content, 'plain'))
        self.smtpserver.send_message(msg)
        self.smtpserver.close()
