import msnotifier.bot.siteMonitor as siteMonitor
import threading
import msnotifier.messenger as messenger
import web.app

class Sending(threading.Thread):
    def __init__(self,changes):
        threading.Thread.__init__(self)
        self.changes =changes
    def run(self):
        for item in  self.changes:
            # z itema wyciągamy alert_id i content
            content=item.content
            alert_id=item[0]
            dboutput=web.app.get_items_for_messaging(alert_id)
            alertwebpage=dboutput[0].page
            mail=dboutput[2].email
            msng=dboutput[2].messenger
            discord=dboutput[2].discord
            if mail==True:
                email=dboutput[1].email
                notifier=messenger.mail_chat()
                notifier.log_into(email,"")
                notifier.message_myself(content,alertwebpage)
            if msng==True:
                fblogin=dboutput[1].fb_login
                fbpass=dboutput[1].fb_passw
                notifier=messenger.mail_chat()
                notifier.log_into(fblogin,fbpass)
                notifier.message_myself(content,alertwebpage)
            if discord==True:
                web.app.add_to_changes(item)




class Opakowanie(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.alerts=[]
    def delete_alert(self,alert_id):
        for alert in self.alerts:
            if alert[0]==alert_id:
                self.alerts.remove(alert)
                return 1
        return -1

    def add_alert(self,alert_id,adr):
        self.alerts.append((alert_id,adr))
    def run(self):
        while(True):
            changes=siteMonitor.getdiffs(["h1", "h2"],self.alerts,50)
            if changes!=0:
                Sending(changes).start()

