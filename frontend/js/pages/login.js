import { login, getCurrentUser } from '../services/auth-admin.js';
import { session } from '../session.js';
import { DEMO_LOGIN } from '../config.js';
import { $, esc, field } from '../ui.js';

export async function render(main) {
  main.innerHTML = `
    <section class="login">
      <h1>Sign in to the gym console</h1>
      <p class="lede">
        Signing in calls <code>auth-admin-service</code> for a JWT. Every later request sends that token
        to the other services, which check it on their own. Watch the Network panel.
      </p>
      <form class="form" id="login-form">
        ${field('Email', `<input name="email" type="email" autocomplete="username" required value="${esc(DEMO_LOGIN.email)}">`)}
        ${field('Password', `<input name="password" type="password" autocomplete="current-password" required value="${esc(DEMO_LOGIN.password)}">`)}
        <p class="form-error" role="alert" hidden></p>
        <button type="submit">Sign in</button>
      </form>
      <p class="muted">The seeded owner account is filled in for you.</p>
    </section>`;

  const form = $('#login-form');
  form.onsubmit = async (event) => {
    event.preventDefault();
    const error = $('.form-error', form);
    const button = $('button', form);
    button.disabled = true;
    error.hidden = true;
    try {
      const { data } = await login(form.email.value, form.password.value);
      session.save({ accessToken: data.access_token, refreshToken: data.refresh_token });
      const { data: user } = await getCurrentUser();
      const primary = user.locations.find((l) => l.primary) ?? user.locations[0];
      session.save({ user, locationId: primary?.location_id });
      location.hash = '#/';
    } catch (err) {
      session.clear();
      error.textContent = err.message;
      error.hidden = false;
    } finally {
      button.disabled = false;
    }
  };
}
