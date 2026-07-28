-- migrate:up
DROP PROCEDURE IF EXISTS add_no_show_enabled_datetime_column_to_location;
CREATE PROCEDURE add_no_show_enabled_datetime_column_to_location()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE location ADD COLUMN no_show_enabled_datetime DATETIME NULL DEFAULT NULL;
END;
CALL add_no_show_enabled_datetime_column_to_location();
DROP PROCEDURE add_no_show_enabled_datetime_column_to_location;


-- migrate:down
DROP PROCEDURE IF EXISTS drop_no_show_enabled_datetime_column_from_location;
CREATE PROCEDURE drop_no_show_enabled_datetime_column_from_location()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE location DROP COLUMN no_show_enabled_datetime;
END;
CALL drop_no_show_enabled_datetime_column_from_location();
DROP PROCEDURE drop_no_show_enabled_datetime_column_from_location;

