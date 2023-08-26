# SyncCue

### About

`SyncCue` is an OSC-based python server using the [Twisted](https://twisted.org/) framework, designed to synchronize cues between multiple systems such as Unity, TouchDesigner, Qlab, etc. 
It can also handle MIDI controls with Disklavier, camera input for vision cue detection, and microphone input for score following.

-  Why we use `twisted`?
    
    `twisted` supports various network protocols (including UDP) and operates on an event-driven architecture, enabling it to handle asynchronous network operations.

### How to use

#### Setting Development Environment
Tested on Python 3.11 & Mambaforge

- If you don't have mamba in your environment, it's okay with installing it with `conda` instead.

```bash
$ git clone git@github.com:laurenceyoon/synccue.git
$ cd synccue
$ mamba env create -f environment.yaml
$ mamba activate sync
```

##### Run OSC Server

```bash
# run OSC server with dashboard page
$ python3 app/main.py

# run only OSC server
$ python3 app/main.py --no-dashboard
```

##### Run OSC Client

You can access admin page with [your browser](http://localhost:8501),
Or you can send OSC message with the following code.

```python
OSC_SERVER_IP = "127.0.0.1"
OSC_SERVER_PORT = 9999

osc_client = udp_client.SimpleUDPClient(OSC_SERVER_IP, OSC_SERVER_PORT)
# example on sending /play message
osc_client.send_message("/play", None)
```
