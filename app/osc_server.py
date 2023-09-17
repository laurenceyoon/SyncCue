from pythonosc.osc_packet import OscPacket
from twisted.internet.protocol import DatagramProtocol


class OSCUDPServer(DatagramProtocol):
    def __init__(self):
        self.handlers = {}

    def startProtocol(self):
        local_endpoint = self.transport.getHost()
        print(f"OSC Server is running on {local_endpoint.host}:{local_endpoint.port}")

    def datagramReceived(self, datagram, address):
        parsed_packet = OscPacket(datagram)
        for msg in parsed_packet.messages:
            handler = self.handlers.get(msg.message.address)
            if handler:
                handler(msg.message.address, *msg.message.params)

    def handle_default(self, address, args):
        print(f"Unknown address: {address} with arguments: {args}")

    def add_handler(self, address):
        def decorator(func):
            self.handlers[address] = func
            return func

        return decorator


server = OSCUDPServer()
