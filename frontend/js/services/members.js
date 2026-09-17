// members-service (:5005): members, their profiles, memberships and invoices.
import { api } from '../api.js';

const base = (locationId) => `/locations/${locationId}/members`;

export const listMembers = (locationId, name) => api('members', 'GET', base(locationId), { query: { name } });

export const getMember = (locationId, memberId) => api('members', 'GET', `${base(locationId)}/${memberId}`);

export const createMember = (locationId, member) =>
  api('members', 'POST', base(locationId), {
    // No mail server runs locally. phone_number must be present even when empty.
    body: { location_id: locationId, send_setup_email: false, phone_number: null, ...member },
  });

export const updateMemberProfile = (locationId, memberId, profile) =>
  api('members', 'PUT', `${base(locationId)}/${memberId}/profile`, {
    body: { location_id: locationId, phone_number: null, ...profile },
  });

export const listMemberships = (locationId, memberId) =>
  api('members', 'GET', `${base(locationId)}/${memberId}/memberships`);

export const createMembership = (locationId, memberId, membership, process = false) =>
  api('members', 'POST', `${base(locationId)}/${memberId}/memberships`, {
    query: { process: process || undefined },
    body: { location_id: locationId, member_id: memberId, ...membership },
  });

export const updateMembership = (locationId, memberId, membershipId, change) =>
  api('members', 'PUT', `${base(locationId)}/${memberId}/memberships/${membershipId}`, {
    body: { location_id: locationId, member_id: memberId, membership_id: membershipId, ...change },
  });

export const listInvoices = (locationId, memberId) =>
  api('members', 'GET', `${base(locationId)}/${memberId}/invoices`);
