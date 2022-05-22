import asyncio
import atexit

from sprink.repo import connect, now, ZONES

OFF = 1
ON = 0

try:
    import RPi.GPIO as gpio

    gpio.setmode(gpio.BCM)

    for pin in ZONES.values():
        gpio.setup(pin, gpio.OUT, initial=OFF)

    
    def _gpio_output(pin, state):
        gpio.output(pin, state)

except RuntimeError:
    
    def _gpio_output(pin, state):
        print(f'pin {pin} {"off" if state else "on"}')


async def gpio_output(pin, state):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _gpio_output, pin, state)


@connect
async def on(con, zone):
    cur = await con.execute('select zone from zone_state where end_ is null;')
    active = [row['zone'] for row in await cur.fetchall()]
    for zone_ in active:
        await off(con, zone_)
    await con.execute('insert into zone_state (zone, start) values (?, ?);', (zone, now()))
    await gpio_output(ZONES[zone], ON)
    return active


@connect
async def off(con, zone):
    await gpio_output(ZONES[zone], OFF)
    end = now()
    await con.execute('update zone_state set end_ = ? where zone = ? and end_ is null;', (end, zone))


def _cleanup_gpio():
    for pin in ZONES.values():
        _gpio_output(pin, OFF)


def register_cleanup():
    atexit.register(_cleanup_gpio)


__all__ = ['on', 'off', 'register_cleanup']