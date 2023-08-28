# SyncCue

## About

`SyncCue` is an OSC-based python server using the [Twisted](https://twisted.org/) framework, designed to synchronize cues between multiple systems such as Unity, TouchDesigner, Qlab, etc. 
It can also handle MIDI controls with Disklavier, camera input for vision cue detection, and microphone input for score following.

> Why we use `twisted`?
>
> `twisted` supports various network protocols (including UDP) and operates on an event-driven architecture, enabling it to handle asynchronous network operations.

## How to use

#### Setting Development Environment
Tested on Python 3.11 & Mambaforge

- If you don't have mamba in your environment, it's okay with installing it with `conda` instead.

```bash
$ git clone git@github.com:laurenceyoon/synccue.git
$ cd synccue
$ mamba env create -f environment.yaml
$ mamba activate sync

# add PYTHONPATH to .env file
$ echo "PYTHONPATH=\"$PWD\"" >> .env

# install mongodb & run database
$ brew tap mongodb/brew && \ 
    brew install mongodb-community@7.0 && \
    brew services start mongodb-community@7.0
```

#### Run SyncCue

```bash
# run SyncCue with dashboard page
$ python -m app.main

# run only SyncCue
$ python -m app.main --no-dashboard
```

#### Test OSC Client

You can access admin page with [your browser](http://localhost:8501),
Or you can send OSC message with the following code.

```python
from pythonosc.udp_client import SimpleUDPClient

osc_client = SimpleUDPClient("127.0.0.1", 9999)
# example on sending /play message
osc_client.send_message("/play", None)
```
