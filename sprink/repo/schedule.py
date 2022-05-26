import json

from crontab import CronTab

from sprink.repo import now, connect, ZONES


@connect(cache=True)
async def get(con, schedule_id = None):
    if schedule_id is not None:
        cur = await con.execute('select * from schedule where id = ?;', (schedule_id,))
        row = await cur.fetchone()
        if row:
            schedule = dict(row)
            schedule['zones'] = json.loads(schedule['zones'])
            return schedule
    else:
        cur = await con.execute('select * from schedule order by updated desc;')
        schedules = []
        for schedule in map(dict, await cur.fetchall()):
            schedule['zones'] = json.loads(schedule['zones'])
            schedules.append(schedule)
        return schedules


@connect(commit=True)
async def create(con, schedule):
    created = updated = now()
    if schedule.get('cron'):
        CronTab(schedule['cron'])
        cron = schedule['cron']
    else:
        return await update(con, 1, schedule)
    duration = schedule['duration']
    zones = schedule['zones']
    assert all(zone in ZONES for zone in zones)
    cur = await con.execute(
        'insert into schedule (cron, duration, zones, disabled, created, updated) '
        'values (?, ?, ?, ?, ?, ?);',
        (cron, duration, json.dumps(zones), 0, created, updated)
    )
    cur = await con.execute('select id from schedule where created = ?;', (created,))
    schedule_id = (await cur.fetchone())['id']
    return await get(con, schedule_id)


@connect(commit=True)
async def update(con, schedule_id, schedule):
    updated = now()
    if schedule.get('cron'):
        CronTab(schedule['cron'])
        cron = schedule['cron']
    else:
        cron = None
    duration = schedule['duration']
    zones = schedule['zones']
    disabled = schedule.get('disabled', 0)
    assert all(zone in ZONES for zone in zones)
    await con.execute(
        'update schedule set cron = ?, duration = ?, zones = ?, disabled = ?, updated = ? where id = ?',
        (cron, duration, json.dumps(zones), disabled, updated, schedule_id)
    )
    return await get(con, schedule_id)


@connect(commit=True)
async def delete(con, schedule_id):
    if schedule_id == 1:
        await con.execute('update schedule set updated = 0 where id = 1;');
        return True
    else:
        schedule = await get(schedule_id)
        if schedule:
            await con.execute('delete from schedule where id = ?;', (schedule_id,))
            return True
        return False


async def get_active():
    schedules = await get()
    for schedule in schedules:
        if schedule['disabled'] != -1 and schedule['disabled'] < now():
            if schedule['cron']:
                cron = CronTab(schedule['cron'])
                prev = cron.previous(default_utc=True) * 1000
            else:
                prev = schedule['updated'] - now()
            duration = schedule['duration']
            for zone in schedule['zones']:
                prev += (duration * 60_000)
                if prev > 0:
                    return {
                        'schedule_id': schedule['id'],
                        'zone': zone,
                        'end': int(now() + prev),
                        'manual': not schedule['cron']
                    }


__all__ = ['get', 'get_active', 'create', 'update', 'delete']