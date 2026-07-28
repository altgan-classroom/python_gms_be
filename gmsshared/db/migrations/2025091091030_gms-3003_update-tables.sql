-- migrate:up

DROP PROCEDURE IF EXISTS update_door_access_log_columns;
CREATE PROCEDURE update_door_access_log_columns()
BEGIN
    alter table door_access_log modify request_type integer not null;
    alter table door_access_log drop column response_datetime;
    alter table door_access_log add response_elapsed_sec float null after response_status_code;
    alter table door_access_log drop column door_id;
    alter table door_access_log drop column group_id;
END;
CALL update_door_access_log_columns();
DROP PROCEDURE update_door_access_log_columns;

UPDATE `_ref_door_access_vendor_auth` set display_name = 'Integration Key' where vendor_id = 1;

-- migrate:down

