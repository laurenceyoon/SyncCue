from pythonosc import udp_client

client = udp_client.SimpleUDPClient("127.0.0.1", 5225)


def _send_osc_message(address, args):
    client.send_message(address, args)
    print(f"==> Sent OSC message with {address} with arguments: {args, type(args)}")


def send_osc_piece_info(title, composer):
    _send_osc_message("/piece_info", [title, composer])

def send_osc_intro():
    _send_osc_message("/intro", "")
    
def send_osc_outro():
    _send_osc_message("/outro", "")


def send_osc_start():
    _send_osc_message("/start", 1)


def send_osc_detect(duration):
    _send_osc_message("/detect", str(duration))


def send_osc_playback(piece_number):
    _send_osc_message("/playback", str(piece_number))


def send_osc_end():
    _send_osc_message("/end", 1)
