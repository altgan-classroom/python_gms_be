// Tokens and the chosen location survive a page reload. Nothing here is secret beyond the JWTs.
const KEY = 'gms-console-session';

function load() {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || {};
  } catch {
    return {};
  }
}

export const session = {
  ...load(),

  save(patch) {
    Object.assign(this, patch);
    const { accessToken, refreshToken, user, locationId } = this;
    try {
      localStorage.setItem(KEY, JSON.stringify({ accessToken, refreshToken, user, locationId }));
    } catch {
      // Private mode: the session just won't survive a reload.
    }
  },

  clear() {
    this.save({ accessToken: null, refreshToken: null, user: null, locationId: null });
  },

  get location() {
    return this.user?.locations?.find((l) => l.location_id === this.locationId);
  },
};
