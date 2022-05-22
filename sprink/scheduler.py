import time
import asyncio
import json

from sprink.repo.zone import on as zone_on, off as zone_off, register_cleanup
from sprink.repo.schedule import get_active

from traceback import print_exc

# _crons = {}


# async def get_active_zone():
#     now = time.time()
#     schedules = list(sorted(await repo.get(), key=lambda s: s['updated']))[::-1]
#     ms = None
#     for s in schedules:
#         if s.get('cron') is None:
#             if ms is None:
#                 ms = s
#             else:
#                 await repo.delete(s['id'])
#     if ms is not None:
#         end = ms['updated'] + sum(z['duration'] for z in ms['zones']) * 60
#         if end < now:
#             await repo.delete(ms['id'])
#         else:
#             a = ms['updated']
#             for z in ms['zones']:
#                 a += (z['duration'] * 60)
#                 if a > now:
#                     return z['zone'], a, True
#     for s in schedules:
#         if 'cron' in s:
#             if s['cron'] in _crons:
#                 ct = _crons[s['cron']]
#             else:
#                 try:
#                     ct = CronTab(s['cron'])
#                 except ValueError as e:
#                     print(e)
#                     continue
#                 _crons[s['cron']] = ct
#             p = ct.previous(default_utc=True)
#             for z in s['zones']:
#                 p += (z['duration'] * 60)
#                 if p > 0:
#                     return z['zone'], now + p, False
#     return None, None, None


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

