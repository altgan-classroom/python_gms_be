-- migrate:up
DROP PROCEDURE IF EXISTS add_discount_percent_column_to_invoice_item;
CREATE PROCEDURE add_discount_percent_column_to_invoice_item()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE invoice_item ADD COLUMN discount_percent FLOAT NULL DEFAULT 0;
END;
CALL add_discount_percent_column_to_invoice_item();
DROP PROCEDURE add_discount_percent_column_to_invoice_item;


-- migrate:down
DROP PROCEDURE IF EXISTS drop_discount_percent_column_from_invoice_item;
CREATE PROCEDURE drop_discount_percent_column_from_invoice_item()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE invoice_item DROP COLUMN discount_percent;
END;
CALL drop_discount_percent_column_from_invoice_item();
DROP PROCEDURE drop_discount_percent_column_from_invoice_item;
