// One entry per backend container. The browser calls each one directly on its published port,
// so the inspector shows exactly which microservice answered.
const host = `${location.protocol}//${location.hostname}`;

export const SERVICES = {
  auth: { name: 'auth-admin-service', port: 5004, base: `${host}:5004/api/v1.1` },
  members: { name: 'members-service', port: 5005, base: `${host}:5005/api/v2/members` },
  plans: { name: 'plans-classes-service', port: 5006, base: `${host}:5006/api/v1` },
  reports: { name: 'reports-service', port: 5008, base: `${host}:5008/api/v1/reports` },
};

export const DEMO_LOGIN = { email: 'owner@demo.gym', password: 'Test@1234' };
