-- migrate:up

DROP PROCEDURE IF EXISTS add_door_access_unlock_to_location;
CREATE PROCEDURE add_door_access_unlock_to_location()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE location
    ADD COLUMN door_access_unlock_doors BOOLEAN DEFAULT FALSE;
END;
CALL add_door_access_unlock_to_location();
DROP PROCEDURE add_door_access_unlock_to_location;


-- migrate:down

DROP PROCEDURE IF EXISTS drop_door_access_unlock_from_location;
CREATE PROCEDURE drop_door_access_unlock_from_location()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE location
    DROP COLUMN door_access_unlock_doors;
END;
CALL drop_door_access_unlock_from_location();
DROP PROCEDURE drop_door_access_unlock_from_location;
