// plans-classes-service (:5006): plans, the class schedule and class bookings.
import { api } from '../api.js';

export const listPlans = (locationId) => api('plans', 'GET', `/plans/locations/${locationId}/plans`);

export const createPlan = (locationId, plan) =>
  api('plans', 'POST', `/plans/locations/${locationId}/plans`, { body: { location_id: locationId, ...plan } });

export const getPlan = (locationId, planId) => api('plans', 'GET', `/plans/locations/${locationId}/plans/${planId}`);

// PUT expects the whole plan, so callers send back what getPlan returned with their changes applied.
export const updatePlan = (locationId, plan) =>
  api('plans', 'PUT', `/plans/locations/${locationId}/plans/${plan.plan_id}`, { body: plan });

// Soft delete: the plan stays on existing memberships with status Cancelled.
export const deletePlan = (locationId, planId) =>
  api('plans', 'DELETE', `/plans/locations/${locationId}/plans/${planId}`);

// A class access group links plans to classes: a member can book a class only if their plan is in
// one of the class's groups.
export const listAccessGroups = (locationId) => api('plans', 'GET', `/classes/locations/${locationId}/class_access_groups`);

export const createAccessGroup = (locationId, name) =>
  api('plans', 'POST', `/classes/locations/${locationId}/class_access_groups`, { body: { location_id: locationId, name } });

// Dates are local gym time, "YYYY-MM-DD HH:MM:SS". The service converts them to UTC.
export const listClasses = (locationId, startDate, endDate) =>
  api('plans', 'GET', `/classes/locations/${locationId}/classes`, { query: { start_date: startDate, end_date: endDate } });

export const createClass = (locationId, session) =>
  api('plans', 'POST', `/classes/locations/${locationId}/classes`, { body: { location_id: locationId, ...session } });

export const cancelClass = (locationId, classId, classTime) =>
  api('plans', 'DELETE', `/classes/locations/${locationId}/classes/${classId}`, {
    query: { class_time: classTime, update_type: 1 },
  });

export const listBookings = (locationId, classId, classTime) =>
  api('plans', 'GET', `/classes/locations/${locationId}/classes/${classId}/bookings`, { query: { class_time: classTime } });

export const bookClass = (locationId, classId, classTime, memberId) =>
  api('plans', 'POST', `/classes/locations/${locationId}/classes/${classId}/bookings`, {
    body: { location_id: locationId, class_id: classId, class_time: classTime, member_id: memberId },
  });

export const checkIn = (locationId, classId, bookingId, time) =>
  api('plans', 'PUT', `/classes/locations/${locationId}/classes/${classId}/bookings/${bookingId}`, {
    body: { member_checked_in_time: time },
  });

// Keeps the booking row and stamps cancellation_time on it.
export const cancelBooking = (locationId, classId, bookingId) =>
  api('plans', 'DELETE', `/classes/locations/${locationId}/classes/${classId}/bookings/${bookingId}`);
