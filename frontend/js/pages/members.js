import { session } from '../session.js';
import { rows } from '../api.js';
import { listMembers, createMember } from '../services/members.js';
import { $, esc, table, field, openForm, toast } from '../ui.js';

export async function render(main) {
  main.innerHTML = `
    <header class="page-head">
      <div>
        <h1>Members</h1>
        <p class="lede">Everyone who has joined or enquired at this location.</p>
      </div>
      <button id="add-member">Add member</button>
    </header>
    <form class="search" id="search" role="search">
      <label class="visually-hidden" for="q">Search by name</label>
      <input id="q" name="q" type="search" placeholder="Search by name">
      <button class="ghost" type="submit">Search</button>
    </form>
    <div id="results"></div>`;

  const results = $('#results');
  const load = async (name) => {
    const list = rows(await listMembers(session.locationId, name));
    results.innerHTML = table(
      [
        { label: 'Name', html: (m) => `<a href="#/members/${m.member_id}">${esc(m.member_name)}</a>` },
        { label: 'Type', html: (m) => `<span class="pill pill-${esc(m.contact_type?.toLowerCase())}">${esc(m.contact_type)}</span>` },
        { label: 'Plans', html: (m) => esc(parsePlans(m.membership_status).join(', ')) },
        { label: 'Email', key: 'email' },
        { label: 'Joined', key: 'create_datetime' },
      ],
      list,
      { empty: name ? `No members match "${name}".` : 'No members yet. Add the first one.' },
    );
  };

  $('#search').onsubmit = (e) => {
    e.preventDefault();
    load($('#q').value.trim()).catch((err) => toast(err.message, 'error'));
  };
  $('#add-member').onclick = addMemberForm;
  await load();
}

// membership_status arrives as a JSON-encoded string, e.g. "[\"Full Membership\"]".
function parsePlans(value) {
  try {
    return JSON.parse(value) ?? [];
  } catch {
    return [];
  }
}

function addMemberForm() {
  openForm({
    title: 'Add member',
    submit: 'Add member',
    fields: `
      <div class="row">
        ${field('First name', '<input name="first_name" required>')}
        ${field('Last name', '<input name="last_name" required>')}
      </div>
      ${field('Email', '<input name="email" type="email" required>')}
      ${field('Phone', '<input name="phone_number" type="tel" placeholder="+15551234567">')}
      ${field('Start date', '<input name="start_date" type="date">')}`,
    onSubmit: async (member) => {
      const { data } = await createMember(session.locationId, member);
      toast(`${member.first_name} ${member.last_name} added`);
      location.hash = `#/members/${data.id}`;
    },
  });
}
