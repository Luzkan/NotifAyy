
from abc import ABC, abstractmethod

import fbchat
from fbchat import ThreadType

def retry_logging(func):
    def wrapper(*args,**kwargs):
        pass
    pass

class Notifier(ABC):
    """
    Each distinct product of a product family should have a base interface. All
    variants of the product must implement this interface.
    """

    @abstractmethod
    def log_into(self,login,password) -> int:
        pass


    @abstractmethod
    def message_myself(self,content) -> int:
        pass



class fb_chat(Notifier):
    client: fbchat.Client
    def log_into(self,login,password):
        try:
            self.client = fbchat.Client("notifaay@gmail.com", "TestTest123")
        except:
            return 0
        return 1

    def message_myself(self, content):
        sent=self.client.sendMessage(content, thread_id=self.client.uid,thread_type=ThreadType.USER)
        if sent:
            return 1
        else:
            return 0
class telegram_chat(Notifier):
    def log_into(self,login,password):
        pass
    def message_myself(self, content):
        pass
class discord_chat(Notifier):
    def log_into(self, login, password):
        pass

    def message_myself(self, content):
        pass
class mail_chat(Notifier):
    def log_into(self, login, password):
        pass

    def message_myself(self, content):
        pass

