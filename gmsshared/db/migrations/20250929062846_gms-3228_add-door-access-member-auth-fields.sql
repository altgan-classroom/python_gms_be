-- migrate:up

DROP PROCEDURE IF EXISTS add_door_access_auth_to_member_profile;
CREATE PROCEDURE add_door_access_auth_to_member_profile()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE member_profile
    ADD COLUMN door_access_auth_info JSON,
    ADD COLUMN door_access_auth_status INT;
END;
CALL add_door_access_auth_to_member_profile();
DROP PROCEDURE add_door_access_auth_to_member_profile;


-- migrate:down

DROP PROCEDURE IF EXISTS drop_door_access_auth_from_member_profile;
CREATE PROCEDURE drop_door_access_auth_from_member_profile()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE member_profile
    DROP COLUMN door_access_auth_info,
    DROP COLUMN door_access_auth_status;
END;
CALL drop_door_access_auth_from_member_profile();
DROP PROCEDURE drop_door_access_auth_from_member_profile;