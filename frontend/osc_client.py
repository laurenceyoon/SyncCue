from twisted.internet import reactor
from pythonosc import udp_client

class OSCClient:
    def __init__(self, host='127.0.0.1', port=9999):
        self.client = udp_client.SimpleUDPClient(host, port)

    def send_message(self, address, value=None):
        self.client.send_message(address, value)
