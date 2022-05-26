const ZoneControl = {
  props: ['zones', 'zoneActive'],
  setup: () => {
    return {
      click: function (zone) {
        if (this.zoneActive.zone === zone) {
          repo.schedule.del(1);
        } else {
          repo.schedule.manual(zone);
        }
      }
    }
  },
  template: `
    <div id="zone-control">
      <div  
        v-for="zone in zones" 
        :class="{ 
          manual: true, 
          active: zoneActive.zone === zone,
          manual: zoneActive.manual
        }"
        @click="click(zone)">
          <span>{{ zone }}</span>
      </div>
    </div>
  `
};

const ZoneTimer = {
  props: ['zoneActive'],
  setup: function (props) {
    const data = Vue.reactive({ count: '-' });
    let timer;
    Vue.watch(() => props.zoneActive, (zone) => {
      if (zone.end) {
        clearInterval(timer);
        timer = setInterval(() => {
          let now = (new Date()).getTime();
          let count = Math.round(zone.end - now);
          if (0 >= count) {
            data.count = '-';
            clearInterval(timer);
          } else {
            data.count = `${Math.round(count / 1000)}`;
          }
        }, 1000);
      } else {
        clearInterval(timer);
        data.count = '-'
      }
    })
    return data;
  },
  template: `
    <div id="zone-timer">{{ count }}</div>
  `
};

const Schedule = {
  props: ['zones', 'schedule', 'schedules'],
  setup: function (props) {
    const isNew = props.schedule === undefined;
    let hasChanged = false;

    const canPersist = () => {
      let b = (
        schedule.cron.length > 0 &&
        schedule.duration &&
        schedule.duration > 0 && 
        schedule.zones.length > 0 &&
        (isNew || hasChanged) &&
        util.isCronValid(schedule.cron)
      )
      return b;
    }

    const schedule = isNew ? Vue.reactive({
      cron: '',
      duration: 10,
      zones: []
    }) : props.schedule;

    const update = (force) => {
      if (force || canPersist()) {
        !isNew && repo.schedule.update(schedule);
        hasChanged = false;
      }
    }

    const updateForm = (key, value) => {
      schedule[key] = value;
      hasChanged = true;
    }

    const updateZones = (zone) => {
      if (schedule.zones.indexOf(zone) === -1) {
        schedule.zones.push(zone);
        schedule.zones.sort();
      } else {
        schedule.zones = schedule.zones.filter(z => z !== zone);
      }
      hasChanged = true;
    }

    const onDisable = () => {
      repo.schedule.disable(schedule)
        .then(({ disabled }) => {
          schedule.disabled = disabled
        })
    }

    const onDelete = () => {
      console.log(props.schedules);
      repo.schedule.del(schedule.id)
        .then(() => {
          props.schedules.splice(props.schedules.indexOf(schedule), 1)
        })
    }

    const data = {
      isNew,
      updateForm,
      updateZones,
      update,
      onDisable,
      onDelete,
      canPersist,
      isCronValid: util.isCronValid
    }

    if (isNew) {
      return {
        ...data,
        schedule,
        create: () => {
          if (canPersist()) {
            repo.schedule.create(schedule)
              .then((data) => {
                props.schedules.unshift(data);
                schedule.cron = '';
                schedule.duration = 10;
                schedule.zones = [];
              })
          }
        }
      }
    } else {
      return data
    }
  },
  template: `
    <div class="schedule">
      <div>
        <input 
          type="text" 
          placeholder="cron"
          :class="{
            invalid: schedule.cron.length && !isCronValid(schedule.cron)
          }"
          :value="schedule.cron" 
          @input="event => updateForm('cron', event.target.value)"
        />
        <input 
          type="number" 
          placeholder="duration"
          :class="{
            invalid: !schedule.duration || schedule.duration <= 0
          }"
          :value="schedule.duration"
          @input="event => updateForm('duration', Number(event.target.value))"
        />
      </div>
      <div class="zones">
        <div 
          v-for="zone in zones" 
          :class="{
            selected: schedule.zones.indexOf(zone) !== -1
          }"
          @click="() => updateZones(zone)"
        >
          <span>{{ zone }}</span>
        </div>
      </div>
      <div v-if="isNew" class="control">
        <button @click="create" :class="{ disabled: !canPersist() }">create</button>
      </div>
      <div v-else class="control">
        <button @click="() => update()" :class="{ disabled: !canPersist() }">update</button>
        <button @click="onDisable" :class="{ active: schedule.disabled }">disable</button>
        <button @click="onDelete">delete</button>
      </div>
    </div>
  `
};