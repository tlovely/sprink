import asyncio
import json

from sprink.repo.zone import on as zone_on, off as zone_off, register_cleanup
from sprink.repo.schedule import get_active

from traceback import print_exc


async def noop(*args, **kwargs):
    pass


def zone_event(zone: str, state: str, duration: int = None, manual: bool = None) -> str:
    return json.dumps({
        "zone": zone,
        "end": duration,
        "state": state,
        "manual": manual
    })


async def manage_zones(event_fn=noop):
    register_cleanup()
    last_zone = None
    while True:
        try:
            await asyncio.sleep(0.25)
            active = await get_active()
            active_zone = active['zone'] if active else None
            if last_zone != active_zone: 
                if active_zone is not None:
                    for zone in await zone_on(active_zone):
                        await event_fn(zone_event(zone, "off"))
                    await event_fn(zone_event(active_zone, "on", active['end'], active['manual']))
                elif last_zone:
                    await zone_off(last_zone)
                    await event_fn(zone_event(last_zone, "off"))
                last_zone = active_zone
        except Exception as e:
            print_exc()

