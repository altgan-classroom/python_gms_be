-- migrate:up

DROP PROCEDURE IF EXISTS add_column_to_member_profile;
CREATE PROCEDURE add_column_to_member_profile()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE member_profile ADD COLUMN door_access_user_id varchar(100) NULL;
END;
CALL add_column_to_member_profile();
DROP PROCEDURE add_column_to_member_profile;

-- migrate:down

