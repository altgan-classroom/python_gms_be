-- migrate:up
ALTER TABLE door_access_door
    RENAME COLUMN door_onboarding_status_type_id TO door_access_door_status;

-- migrate:down

