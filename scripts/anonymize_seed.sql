-- Replaces every personal or customer value copied from stage with fictional data.
-- Run against the seeded database before dumping it to gmsshared/db/init.sql. Safe to rerun.

UPDATE gym
SET name = 'Riverside Strength', logo_url = NULL, company_name = NULL, company_website = NULL;

UPDATE location
SET name = 'Riverside Strength',
    address_1 = '100 Example Street',
    address_2 = '',
    city = 'Springfield',
    state = 'TX',
    zip = '75001',
    cs_phone = '+10000000000',
    cs_email = 'frontdesk@demo.gym',
    payrix_merchant_id = CONCAT('p1_mer_demo', id),
    payrix_entity_id = NULL,
    payrix_group_id = NULL,
    logo_url = NULL,
    door_access_auth_error = NULL;

-- Names are assigned by user_id order, so the owner (lowest id) is always the first entry.
UPDATE user_profile p
JOIN (SELECT user_id, ROW_NUMBER() OVER (ORDER BY user_id) AS n FROM user_profile) ranked ON ranked.user_id = p.user_id
JOIN (
  SELECT 1 AS n, 'Jordan' AS first_name, 'Blake' AS last_name UNION ALL SELECT 2, 'Front', 'Desk'
  UNION ALL SELECT 3, 'Avery', 'Stone' UNION ALL SELECT 4, 'Blair', 'Hughes' UNION ALL SELECT 5, 'Casey', 'Morgan'
  UNION ALL SELECT 6, 'Dana', 'Brooks' UNION ALL SELECT 7, 'Eli', 'Warren' UNION ALL SELECT 8, 'Frankie', 'Hale'
  UNION ALL SELECT 9, 'Gray', 'Porter' UNION ALL SELECT 10, 'Harper', 'Quinn' UNION ALL SELECT 11, 'Indy', 'Reeves'
  UNION ALL SELECT 12, 'Jamie', 'Sutton' UNION ALL SELECT 13, 'Kai', 'Turner' UNION ALL SELECT 14, 'Lane', 'Vaughn'
  UNION ALL SELECT 15, 'Micah', 'Walsh' UNION ALL SELECT 16, 'Noel', 'Young' UNION ALL SELECT 17, 'Oakley', 'Price'
  UNION ALL SELECT 18, 'Parker', 'Reid' UNION ALL SELECT 19, 'Quinn', 'Foster' UNION ALL SELECT 20, 'Reese', 'Garner'
  UNION ALL SELECT 21, 'Sage', 'Holland' UNION ALL SELECT 22, 'Tatum', 'Irwin' UNION ALL SELECT 23, 'Umber', 'Jennings'
  UNION ALL SELECT 24, 'Val', 'Keller' UNION ALL SELECT 25, 'Wren', 'Lawson' UNION ALL SELECT 26, 'Xen', 'Mercer'
  UNION ALL SELECT 27, 'Yael', 'Nolan' UNION ALL SELECT 28, 'Zion', 'Osborne' UNION ALL SELECT 29, 'Arden', 'Pike'
  UNION ALL SELECT 30, 'Bay', 'Ramsey' UNION ALL SELECT 31, 'Corin', 'Shaw' UNION ALL SELECT 32, 'Drew', 'Tate'
  UNION ALL SELECT 33, 'Emery', 'Upton' UNION ALL SELECT 34, 'Finley', 'Vance' UNION ALL SELECT 35, 'Gale', 'Whitaker'
  UNION ALL SELECT 36, 'Hollis', 'York' UNION ALL SELECT 37, 'Ira', 'Abbott' UNION ALL SELECT 38, 'Jules', 'Barton'
  UNION ALL SELECT 39, 'Kit', 'Carver' UNION ALL SELECT 40, 'Logan', 'Dalton' UNION ALL SELECT 41, 'Marlow', 'Ellis'
  UNION ALL SELECT 42, 'Nico', 'Fleming' UNION ALL SELECT 43, 'Ollie', 'Grant' UNION ALL SELECT 44, 'Peyton', 'Hayes'
  UNION ALL SELECT 45, 'Robin', 'Ingram' UNION ALL SELECT 46, 'Skyler', 'Jensen' UNION ALL SELECT 47, 'Toby', 'Knox'
  UNION ALL SELECT 48, 'Remy', 'Lowe' UNION ALL SELECT 49, 'Shay', 'Marsh' UNION ALL SELECT 50, 'Rowan', 'Nash'
) fake ON fake.n = 1 + MOD(ranked.n - 1, 50)
SET p.first_name = fake.first_name,
    p.last_name = fake.last_name,
    p.middle_name = NULL,
    p.preferred_name = NULL,
    p.photo_url = NULL,
    p.about = NULL,
    p.birth_date = '2000-01-01',
    p.address_street = '100 Example Street',
    p.address_street_2 = NULL,
    p.address_city = 'Springfield',
    p.address_state = 'TX',
    p.address_zip = '75001',
    p.phone_number = '+10000000000',
    p.emergency_first_name = NULL,
    p.emergency_last_name = NULL,
    p.emergency_phone_number = NULL,
    p.guardian_first_name = NULL,
    p.guardian_last_name = NULL,
    p.guardian_phone_number = NULL;

UPDATE user
SET email = IF(role_type_id = 1, 'owner@demo.gym', CONCAT('u', id, '@demo.gym'));

-- door_access_auth_info held vendor credentials (email + secret) for real people.
UPDATE member_profile
SET payrix_customer_id = IF(payrix_customer_id IS NULL, NULL, CONCAT('p1_cus_demo', user_id)),
    door_access_user_id = NULL,
    door_access_credential = NULL,
    door_access_credential_id = NULL,
    door_access_auth_info = NULL,
    favourite_gym_clothing_website = NULL,
    favourite_website = NULL,
    favourite_restaurant = NULL;
