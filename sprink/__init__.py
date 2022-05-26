import asyncio

from typing import Optional, List

from toolz import curry
from aiohttp.web import (
    Application,
    RouteTableDef,
    json_response, 
    middleware,
    FileResponse,
    StreamResponse,
    HTTPFound,
    run_app
)

from sprink.repo import schedule, user, ZONES
from sprink.scheduler import manage_zones

routes = RouteTableDef()


@curry
async def serve_file(file_, request):
    return FileResponse(file_)


@middleware
async def handle_auth(request, handler):
    token = request.cookies.get('sprink')
    if token is None or not (await user.get(token=token)):
        path = request.path
        if path.startswith('/api'):
            if path != '/api/login':
                return json_response({'error': 'unauthorized'}, status=401)
        elif path != '/login':
            raise HTTPFound('/login')
    return await handler(request)


@routes.get('/api/zone')
async def get_zones(request):
    return json_response(list(ZONES.keys()))


@routes.post('/api/schedule')
async def post_schedule(request):
    return json_response(await schedule.create(await request.json()))


@routes.put('/api/schedule/{schedule_id}')
async def put_schedule(request):
    schedule_id = request.match_info['schedule_id']
    return json_response(await schedule.update(int(schedule_id), await request.json()))


@routes.put('/api/schedule/{schedule_id}/disable')
async def put_schedule_disable(request):
    schedule_id = int(request.match_info['schedule_id'])
    schedule_ = await schedule.get(schedule_id)
    schedule_['disabled'] = 0 if schedule_['disabled'] else -1
    return json_response(await schedule.update(schedule_id, schedule_))


@routes.delete('/api/schedule/{schedule_id}')
async def delete_schedule(request):
    schedule_id = request.match_info['schedule_id']
    return json_response(await schedule.delete(int(schedule_id)))


@routes.get('/api/schedule')
async def get_schedules(request):
    return json_response(await schedule.get())


@routes.get('/api/schedule/{schedule_id}')
async def get_schedule(request):
    schedule_id = request.match_info['schedule_id']
    return json_response(await schedule.get(int(schedule_id)))


@routes.post('/api/login')
async def login_client(request):
    payload = await request.json()
    token = await user.validate(payload['username'], payload['password'])
    if token is None:
        return json_response({'error': 'bad credentials'}, status=401)
    else:
        response = json_response({'token': token})
        response.set_cookie('sprink', token)
        return response


@routes.get('/api/events')
async def lawn_events(request):
    response = StreamResponse()
    response.headers['content-type'] = 'text/event-stream'
    await response.prepare(request)
    request.app['event_listeners'].append(response.write)
    if app['event_last']:
        await response.write(app['event_last'])
    while response.write in request.app['event_listeners']:
        await asyncio.sleep(1)


routes.static('/static', 'sprink/static')

routes.get('/login')(serve_file('sprink/html/login.html'))
routes.get('/')(serve_file('sprink/html/client.html'))


async def on_startup(app):
    app['event_listeners'] = []
    app['event_last'] = None

    async def write_event(event):
        event = f'event: zone_state\ndata: {event}\n\n'.encode()
        app['event_last'] = event
        for w in app['event_listeners'][:]:
            try:
                await w(event)
            except Exception:
                app['event_listeners'].remove(w)

    app['zone_manager'] = app.loop.create_task(manage_zones(write_event))


async def on_cleanup(app):
    app['zone_manager'].cancel()
    await app['zone_manager']


app = Application(middlewares=[handle_auth])
app.on_startup.append(on_startup)
app.on_cleanup.append(on_cleanup)
app.router.add_routes(routes)


if __name__ == '__main__':
    run_app(app)