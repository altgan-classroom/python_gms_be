-- migrate:up

CREATE TABLE class_access_group_door(
    class_access_group_id BIGINT NOT NULL,
    door_id BIGINT NOT NULL,
    FOREIGN KEY (class_access_group_id) REFERENCES class_access_group(id),
    FOREIGN KEY (door_id) REFERENCES door_access_door(id)
);


DROP PROCEDURE IF EXISTS update_door_access_log_columns;
CREATE PROCEDURE update_door_access_log_columns()
BEGIN
    alter table class_access_group add column door_access_group_id varchar(100) null;
    alter table class_access_group add column door_access_group_status int null default 0;
END;
CALL update_door_access_log_columns();
DROP PROCEDURE update_door_access_log_columns;

-- migrate:down

