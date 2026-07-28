-- migrate:up
DROP PROCEDURE IF EXISTS add_access_times_columns;
CREATE PROCEDURE add_access_times_columns()
BEGIN
    alter table class_access_group add column door_access_access_times_flag boolean default false;
    alter table class_access_group add column door_access_access_times json null;
END;
CALL add_access_times_columns();
DROP PROCEDURE add_access_times_columns;

-- migrate:down

