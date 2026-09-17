import { session } from '../session.js';
import { rows } from '../api.js';
import { listRooms, createRoom, deleteRoom } from '../services/auth-admin.js';
import { listMembers } from '../services/members.js';
import {
  listClasses, createClass, cancelClass, listBookings, bookClass, checkIn, cancelBooking, listAccessGroups, createAccessGroup,
} from '../services/plans-classes.js';
import { CLASS_TYPES } from '../lookups.js';
import { $, esc, table, field, openForm, options, isoDate, today, nowLocal, weekDays, toast, run } from '../ui.js';

export async function render(main) {
  const locationId = session.locationId;
  const offset = Number(main.dataset.week ?? 0);
  const days = weekDays(offset);

  const [classes, rooms, groups] = await Promise.all([
    listClasses(locationId, `${isoDate(days[0])} 00:00:00`, `${isoDate(days[6])} 23:59:59`),
    listRooms(locationId),
    listAccessGroups(locationId),
  ]);
  const sessions = classes.data?.classes ?? [];
  const range = `${days[0].toLocaleDateString(undefined, { month: 'short', day: 'numeric' })} to ${days[6].toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}`;

  main.innerHTML = `
    <header class="page-head">
      <div>
        <h1>Classes</h1>
        <p class="lede">The schedule and bookings live in plans-classes-service. Rooms come from auth-admin-service.</p>
      </div>
      <div class="head-actions">
        <button class="ghost" id="rooms">Rooms (${rows(rooms).length})</button>
        <button class="ghost" id="groups">Access groups (${rows(groups).length})</button>
        <button id="add-class">Add class</button>
      </div>
    </header>

    <nav class="week-nav" aria-label="Week">
      <button class="ghost small" data-week="-1">Previous week</button>
      <strong>${esc(range)}</strong>
      <button class="ghost small" data-week="1">Next week</button>
    </nav>

    <ol class="week">
      ${days
        .map((day) => {
          const date = isoDate(day);
          const todays = sessions.filter((s) => s.start_time.startsWith(date));
          return `
            <li class="day ${date === today() ? 'is-today' : ''}">
              <h3>${day.toLocaleDateString(undefined, { weekday: 'short' })} <span>${day.getDate()}</span></h3>
              <div class="day-sessions">
              ${todays.length ? '' : '<p class="empty small">No classes</p>'}
              ${todays
                .map(
                  (s) => `
                <button class="session" data-class="${s.class_id}" data-time="${esc(s.start_time)}">
                  <span class="session-time">${esc(s.start_time.slice(11))}</span>
                  <span class="session-name">${esc(s.name)}</span>
                  <span class="session-meta">${s.current_attendance}/${s.attendance_cap} booked</span>
                </button>`,
                )
                .join('')}
              </div>
            </li>`;
        })
        .join('')}
    </ol>
    <section id="bookings" class="panel" hidden></section>`;

  const reload = () => render(main);
  for (const b of main.querySelectorAll('[data-week]')) {
    b.onclick = () => {
      main.dataset.week = offset + Number(b.dataset.week);
      reload();
    };
  }
  $('#rooms').onclick = () => roomsForm(rows(rooms), reload);
  $('#groups').onclick = () => groupsForm(rows(groups), reload);
  $('#add-class').onclick = () => addClassForm(rows(rooms), rows(groups), reload);
  for (const b of main.querySelectorAll('[data-class]')) {
    b.onclick = () => {
      main.querySelectorAll('.session[aria-pressed]').forEach((el) => el.removeAttribute('aria-pressed'));
      b.setAttribute('aria-pressed', 'true');
      const session_ = sessions.find((s) => s.class_id === Number(b.dataset.class) && s.start_time === b.dataset.time);
      showBookings(session_, reload);
    };
  }
}

async function showBookings(clazz, reload) {
  const locationId = session.locationId;
  const classTime = `${clazz.start_time}:00`;
  const panel = $('#bookings');
  const [bookings, members] = await Promise.all([
    run(() => listBookings(locationId, clazz.class_id, classTime)),
    run(() => listMembers(locationId)),
  ]);
  const active = rows(bookings).filter((b) => !b.cancellation_time);
  const clients = rows(members).filter((m) => m.contact_type === 'Client');

  panel.hidden = false;
  panel.innerHTML = `
    <div class="panel-head">
      <h2>${esc(clazz.name)}, ${esc(clazz.start_time)} to ${esc(clazz.end_time.slice(11))}</h2>
      <button class="ghost small danger" id="cancel-class">Cancel this class</button>
    </div>
    <p class="muted">${esc(CLASS_TYPES.find((t) => t.id === clazz.class_type_id)?.name ?? '')}, ${active.length} of ${clazz.attendance_cap} places booked.</p>
    ${table(
      [
        { label: 'Member', html: (b) => `<a href="#/members/${b.user_id}">${esc(b.first_name)} ${esc(b.last_name)}</a>` },
        { label: 'Booked at', key: 'member_registered_time' },
        { label: 'Checked in', html: (b) => esc(b.member_checked_in_time ?? 'Not yet') },
        {
          label: '',
          html: (b) => `<span class="row-actions">
              ${b.member_checked_in_time ? '' : `<button class="ghost small" data-checkin="${b.booking_id}">Check in</button>`}
              <button class="ghost small danger" data-unbook="${b.booking_id}">Cancel booking</button>
            </span>`,
        },
      ],
      active,
      { empty: 'Nobody has booked this class yet.' },
    )}
    <form class="inline-form" id="book">
      <label class="field"><span>Book a member</span>
        <select name="member_id" required>${options(clients, 'member_id', 'member_name')}</select>
      </label>
      <button type="submit">Book</button>
    </form>
    <p class="muted small">Members are listed by members-service. Booking is checked against the member's plans by plans-classes-service.</p>`;

  const refresh = () => showBookings(clazz, reload);
  $('#book', panel).onsubmit = (e) => {
    e.preventDefault();
    run(async () => {
      await bookClass(locationId, clazz.class_id, classTime, Number(e.target.member_id.value));
      await refresh();
    }, 'Member booked');
  };
  for (const b of panel.querySelectorAll('[data-checkin]')) {
    b.onclick = () =>
      run(async () => {
        await checkIn(locationId, clazz.class_id, Number(b.dataset.checkin), nowLocal(session.location));
        await refresh();
      }, 'Checked in');
  }
  for (const b of panel.querySelectorAll('[data-unbook]')) {
    b.onclick = () =>
      run(async () => {
        await cancelBooking(locationId, clazz.class_id, Number(b.dataset.unbook));
        await refresh();
      }, 'Booking cancelled');
  }
  $('#cancel-class', panel).onclick = () =>
    run(async () => {
      await cancelClass(locationId, clazz.class_id, classTime);
      await reload();
    }, 'Class cancelled');
  panel.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'nearest' });
}

function addClassForm(rooms, groups, reload) {
  if (!rooms.length) return toast('Add a room first. Classes need somewhere to happen.', 'error');
  openForm({
    title: 'Add class',
    submit: 'Add class',
    fields: `
      ${field('Name', '<input name="name" required>')}
      <div class="row">
        ${field('Type', `<select name="class_type_id" data-number>${options(CLASS_TYPES, 'id', 'name')}</select>`)}
        ${field('Room', `<select name="room_id" data-number>${options(rooms, 'room_id', 'name')}</select>`)}
      </div>
      <div class="row">
        ${field('Date', `<input name="date" type="date" required value="${today()}">`)}
        ${field('Starts', '<input name="start" type="time" required value="18:00">')}
        ${field('Ends', '<input name="end" type="time" required value="19:00">')}
      </div>
      ${field('Places', '<input name="attendance_cap" type="number" min="1" value="12" required>')}
      ${
        groups.length
          ? field('Access groups', `<select name="class_access_groups" multiple>${options(groups, 'id', 'name')}</select>`, 'Only members whose plan is in a selected group can book.')
          : '<p class="muted">No access groups yet, so nobody will be able to book. Create one from the Access groups button.</p>'
      }`,
    onSubmit: async ({ date, start, end, ...form }) => {
      if (end <= start) throw new Error('The class must end after it starts.');
      await createClass(session.locationId, {
        ...form,
        location_type_id: 1,
        start_time: `${date} ${start}:00`,
        end_time: `${date} ${end}:00`,
        all_day_event: false,
        // Recurring classes are left out: the class list endpoint fails to serialise them.
        recurring: false,
        private_training: false,
      });
      toast(`${form.name} added`);
      await reload();
    },
  });
}

function roomsForm(rooms, reload) {
  const dialog = openForm({
    title: 'Rooms',
    submit: 'Add room',
    fields: `
      ${table(
        [
          { label: 'Room', key: 'name' },
          { label: 'Capacity', key: 'capacity' },
          { label: '', html: (r) => `<button type="button" class="ghost small danger" data-room="${r.room_id}">Delete</button>` },
        ],
        rooms,
        { empty: 'No rooms yet.' },
      )}
      <div class="row">
        ${field('New room', '<input name="name" required>')}
        ${field('Capacity', '<input name="capacity" type="number" min="1">')}
      </div>`,
    onSubmit: async (room) => {
      await createRoom(session.locationId, room);
      toast(`${room.name} added`);
      await reload();
    },
  });
  for (const b of dialog.querySelectorAll('[data-room]')) {
    b.onclick = () =>
      run(async () => {
        await deleteRoom(session.locationId, Number(b.dataset.room));
        dialog.close();
        await reload();
      }, 'Room deleted');
  }
}

function groupsForm(groups, reload) {
  openForm({
    title: 'Access groups',
    submit: 'Add group',
    fields: `
      <p class="muted">Put classes and plans in the same group to let those members book those classes. Assign plans from the Plans page.</p>
      ${table(
        [
          { label: 'Group', key: 'name' },
          { label: 'Active', html: (g) => (g.active ? 'Yes' : 'No') },
        ],
        groups,
        { empty: 'No access groups yet.' },
      )}
      ${field('New group', '<input name="name" required placeholder="All members">')}`,
    onSubmit: async ({ name }) => {
      await createAccessGroup(session.locationId, name);
      toast(`${name} added`);
      await reload();
    },
  });
}
