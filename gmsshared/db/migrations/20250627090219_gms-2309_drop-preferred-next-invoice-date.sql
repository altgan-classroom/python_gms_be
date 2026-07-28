-- migrate:up

DROP PROCEDURE IF EXISTS drop_preferred_column_from_membership;
CREATE PROCEDURE drop_preferred_column_from_membership()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE membership DROP COLUMN preferred_next_invoice_date;
END;
CALL drop_preferred_column_from_membership();
DROP PROCEDURE drop_preferred_column_from_membership;

DROP PROCEDURE IF EXISTS rename_preferred_flag_column;
CREATE PROCEDURE rename_preferred_flag_column()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE membership RENAME COLUMN apply_preferred_next_invoice_date_to_all_invoices TO apply_next_billing_date_to_all_invoices;
END;
CALL rename_preferred_flag_column();
DROP PROCEDURE rename_preferred_flag_column;

-- migrate:down

DROP PROCEDURE IF EXISTS add_preferred_column_to_membership;
CREATE PROCEDURE add_preferred_column_to_membership()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE membership ADD COLUMN preferred_next_invoice_date DATE NULL DEFAULT NULL;
END;
CALL add_preferred_column_to_membership();
DROP PROCEDURE add_preferred_column_to_membership;

DROP PROCEDURE IF EXISTS revert_rename_preferred_flag_column;
CREATE PROCEDURE revert_rename_preferred_flag_column()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE membership RENAME COLUMN apply_next_billing_date_to_all_invoices TO apply_preferred_next_invoice_date_to_all_invoices;
END;
CALL revert_rename_preferred_flag_column();
DROP PROCEDURE revert_rename_preferred_flag_column;