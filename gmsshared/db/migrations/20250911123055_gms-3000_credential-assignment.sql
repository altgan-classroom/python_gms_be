-- migrate:up
DROP PROCEDURE IF EXISTS update_door_access_log_columns;
CREATE PROCEDURE update_door_access_log_columns()
BEGIN

    alter table member_profile add door_access_credential varchar(100) null;
    alter table member_profile add door_access_credential_id varchar(100) null;
    alter table member_profile add door_access_credential_status int null default 1;
END;
CALL update_door_access_log_columns();
DROP PROCEDURE update_door_access_log_columns;

-- migrate:down

