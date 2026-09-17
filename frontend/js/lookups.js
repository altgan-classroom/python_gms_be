// Reference data. The services expose no endpoints for these, so the ids mirror the _ref_* tables
// seeded by gmsshared/db/init.sql.
const list = (names) => Object.entries(names).map(([id, name]) => ({ id: Number(id), name }));

export const ROLE_TYPES = list({ 3: 'Coach', 4: 'Manager', 5: 'Staff' });
export const BILLING_TYPES = list({ 1: 'Recurring', 2: 'Paid in full', 3: 'Session pack', 4: 'Free' });
export const DURATION_TYPES = list({ 1: 'Days', 2: 'Weeks', 3: 'Months', 4: 'Years' });
export const MEMBERSHIP_TYPES = list({ 1: 'Full membership', 2: 'Challenge', 3: 'Limited time pass' });
export const CLASS_TYPES = list({
  1: 'Bootcamp', 2: 'Boxing / Kickboxing', 3: 'Cardio', 4: 'Crossfit', 5: 'HIIT', 6: 'Martial Arts',
  7: 'Semi-Private', 8: 'Spinning', 9: 'Strength Training', 10: 'Yoga / Pilates', 11: 'Private Training',
});
export const MEMBERSHIP_STATUS = { CANCELLED: 2 };

export const REPORTS = [
  { id: 'LOCMEMBCOUNT', name: 'Membership counts', service: 'Operations' },
  { id: 'NEWCONTACTS', name: 'New contacts', service: 'Sales' },
  { id: 'NEWSALES', name: 'New sales', service: 'Sales' },
  { id: 'ATRISKATT', name: 'At-risk attendance', service: 'Operations' },
  { id: 'ATTPERMONTH', name: 'Attendance per month', service: 'Operations' },
  { id: 'MEMBSESSATT', name: 'Member session attendance', service: 'Operations' },
  { id: 'BASICCHURN', name: 'Recurring member churn', service: 'Sales' },
  { id: 'NETREVENUE', name: 'Net revenue', service: 'Financial' },
  { id: 'MTDREVENUE', name: 'Month-to-date revenue', service: 'Financial' },
  { id: 'LASTMONTH', name: 'Last month revenue', service: 'Financial' },
  { id: 'FORECASTED', name: 'Forecasted revenue', service: 'Financial' },
  { id: 'BALANCEFUTURECONTRACT', name: 'Balance and future contract value', service: 'Financial' },
];
