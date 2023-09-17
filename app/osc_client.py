from pythonosc import udp_client


client = udp_client.SimpleUDPClient("127.0.0.1", 5005)


def send_osc_start():
    client.send_message("/start", 1)


def send_osc_detect(duration: float):
    client.send_message("/detect", str(duration))


def send_osc_end():
    client.send_message("/end", 1)
