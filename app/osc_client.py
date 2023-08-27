from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor


class EchoClientUDP(DatagramProtocol):
    def startProtocol(self):
        self.transport.write(b"Hello, server!", ("127.0.0.1", 9999))

    def datagramReceived(self, datagram, address):
        print(f"Received reply: {datagram.decode()}")


# UDP 클라이언트 시작
reactor.listenUDP(0, EchoClientUDP())  # 0은 OS에 무작위 포트 할당을 요청
reactor.run()
