import asyncio

from pythonosc.osc_packet import OscPacket
from twisted.internet.protocol import DatagramProtocol


class OSCUDPServer(DatagramProtocol):
    def __init__(self):
        self.handlers = {}

    def startProtocol(self):
        local_endpoint = self.transport.getHost()
        print(f"OSC Server is running on {local_endpoint.host}:{local_endpoint.port}")

    def datagramReceived(self, datagram, address):
        loop = asyncio.get_event_loop()
        loop.call_soon(
            asyncio.create_task, self._async_datagramReceived(datagram, address)
        )

    async def _async_datagramReceived(self, datagram, address):
        try:
            parsed_packet = OscPacket(datagram)
        except Exception:
            return
        for msg in parsed_packet.messages:
            handler = self.handlers.get(msg.message.address)
            if handler:
                print(
                    f"\n<== Received OSC message with {address[0]}:{address[1]}{msg.message.address} "
                    f"with arguments: {*msg.message.params, type(*msg.message.params)}, datagram packet: {datagram}"
                )
                await handler(msg.message.address, *msg.message.params)

    def handle_default(self, address, args):
        print(f"Unknown address: {address} with arguments: {args}")

    def add_handler(self, address):
        def decorator(func):
            self.handlers[address] = func
            return func

        return decorator


server = OSCUDPServer()
