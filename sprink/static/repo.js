const repo = (() => {

  const get = (path) => {
    return fetch(`/api/${path}`, {
      method: 'GET'
    })
  }

  const post = (path, data) => {
    return fetch(`/api/${path}`, {
      method: 'POST',
      headers: {'content-type': 'application/json'},
      body: JSON.stringify(data)
    })
  }

  const put = (path, data) => {
    return fetch(`/api/${path}`, {
      method: 'PUT',
      headers: {'content-type': 'application/json'},
      body: JSON.stringify(data)
    })
  }

  const del = (path) => {
    return fetch(`/api/${path}`, {
      method: 'DELETE'
    })
  }

  const schedule = {
    get: (id) => get(`schedule/${id}`).then((r) => r.json()),
    del: (id) => del(`schedule/${id}`),
    list: () => get('schedule').then((r) => r.json()),
    create: (schedule) => post('schedule', schedule).then((r) => r.json()),
    update: (schedule) => put(`schedule/${schedule.id}`, schedule).then((r) => r.json()),
    manual: (zone) => {
      return schedule.create({ id: 1, zones: [zone], duration: 1 });
    },
    disable: (schedule) => put(`schedule/${schedule.id}/disable`, {}).then((r) => r.json())
  }

  const zone = {
    list: () => get('zone').then((r) => r.json())
  }

  const events = () => {
    return new EventSource('/api/events');
  }

  return { schedule, zone, events }

})();