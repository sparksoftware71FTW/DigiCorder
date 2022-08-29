import json
from channels.generic.websocket import WebsocketConsumer

class DashboardConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Yeehaw... You are now connected.'
        }))

    # def disconnect(self, code):
    #     return super().disconnect(code)

    # def receive(self, text_data=None, bytes_data=None):
    #     return super().receive(text_data, bytes_data)