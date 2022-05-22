# sprink

Sprink is a sprinkler timer application intended to run on a raspberry pi.

## setup

SSH into the RPi or otherwise open a terminal session.

### clone repo

```bash
git clone git@github.com:tlovely/sprink.git
```

### create zone map

Create a file at `/opt/a/sprink/.zones.json` with your zone to gpio mapping. Below is an example:

```json
{
    "1": 5,
    "2": 6,
    "3": 16,
    "4": 17,
    "5": 22,
    "6": 23
}
```

RPi pinout: https://pinout.xyz/

Wire gpio pins to relay board. The one I used linked [here](https://www.amazon.com/SainSmart-101-70-102-8-Channel-Relay-Module/dp/B0057OC5WK/ref=sr_1_5?crid=AZ2JT3W0H139&keywords=8+channel+relay&qid=1653249595&sprefix=8+channel+relay%2Caps%2C107&sr=8-5)

RPi is capable of powering linked relay module. Connect 5V pin on RPi to VCC and GND pin to GND pin on the relay module.

### final setup

```bash
# install virtual env, initializes database (sqlite), user creation prompt
make setup
```

## run

### development server

```bash
make run-dev
```

Navigate to `http://<rpi-ip>:8000/login`. Or, if running locally, http://localhost:8000/login.

