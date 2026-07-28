-- migrate:up
DROP PROCEDURE IF EXISTS add_block_registrations_column_to_location;
CREATE PROCEDURE add_block_registrations_column_to_location()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE location
    ADD COLUMN block_registrations_on_balance_due BOOLEAN NOT NULL DEFAULT FALSE;
END;
CALL add_block_registrations_column_to_location();
DROP PROCEDURE add_block_registrations_column_to_location;

-- migrate:down
DROP PROCEDURE IF EXISTS drop_block_registrations_column_from_location;
CREATE PROCEDURE drop_block_registrations_column_from_location()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE location
    DROP COLUMN block_registrations_on_balance_due;
END;
CALL drop_block_registrations_column_from_location();
DROP PROCEDURE drop_block_registrations_column_from_location;

