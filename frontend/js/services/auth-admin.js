// auth-admin-service (:5004): login, the signed-in user, locations, rooms and staff.
import { api } from '../api.js';

export const login = (email, password) =>
  api('auth', 'POST', '/auth/login', { body: { email, password }, auth: false });

export const getCurrentUser = () => api('auth', 'GET', '/auth/user');

export const listRooms = (locationId) => api('auth', 'GET', `/admin/locations/${locationId}/rooms`);

export const createRoom = (locationId, room) =>
  api('auth', 'POST', `/admin/locations/${locationId}/rooms`, { body: { location_id: locationId, ...room } });

export const deleteRoom = (locationId, roomId) =>
  api('auth', 'DELETE', `/admin/locations/${locationId}/rooms/${roomId}`);

export const listStaff = (locationId) => api('auth', 'GET', `/admin/locations/${locationId}/users`);

export const createStaff = (locationId, user) =>
  api('auth', 'POST', `/admin/locations/${locationId}/users`, { body: { location_id: locationId, ...user } });
