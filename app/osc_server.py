from pythonosc import osc_packet
from twisted.internet.protocol import DatagramProtocol


class OSCUDPServer(DatagramProtocol):
    def __init__(self):
        self.handlers = {}

    def startProtocol(self):
        local_endpoint = self.transport.getHost()
        print(f"OSC Server is running on {local_endpoint.host}:{local_endpoint.port}")

    def datagramReceived(self, datagram, address):
        try:
            parsed_packet = osc_packet.OscPacket(datagram)

            if isinstance(parsed_packet, osc_packet.OscMessage):
                address = parsed_packet.address
                args = parsed_packet.params

                handler = self.handlers.get(address, self.handle_default)
                handler(address, args)

            elif isinstance(parsed_packet, osc_packet.OscBundle):
                for bundled_msg in parsed_packet.content:
                    if isinstance(bundled_msg, osc_packet.OscMessage):
                        address = bundled_msg.address
                        args = bundled_msg.params

                        handler = self.handlers.get(address, self.handle_default)
                        handler(address, args)

        except Exception as e:
            print(f"Error processing OSC message: {e}")

    def handle_default(self, address, args):
        print(f"Unknown address: {address} with arguments: {args}")

    def add_handler(self, address):
        def decorator(func):
            self.handlers[address] = func
            return func

        return decorator
