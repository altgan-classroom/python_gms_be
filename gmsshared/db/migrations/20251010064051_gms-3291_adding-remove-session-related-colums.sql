-- migrate:up
DROP PROCEDURE IF EXISTS add_columns_to_membership_session;
CREATE PROCEDURE add_columns_to_membership_session()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;

  ALTER TABLE membership_session ADD COLUMN updated_by BIGINT NULL;
  ALTER TABLE membership_session ADD COLUMN notes VARCHAR(250) NULL;
  ALTER TABLE membership_session ADD COLUMN total_amount FLOAT NULL;

END;
CALL add_columns_to_membership_session();
DROP PROCEDURE add_columns_to_membership_session;


-- migrate:down
DROP PROCEDURE IF EXISTS drop_columns_from_membership_session;
CREATE PROCEDURE drop_columns_from_membership_session()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;

  ALTER TABLE membership_session DROP COLUMN updated_by;
  ALTER TABLE membership_session DROP COLUMN notes;
  ALTER TABLE membership_session DROP COLUMN total_amount;

END;
CALL drop_columns_from_membership_session();
DROP PROCEDURE drop_columns_from_membership_session;

