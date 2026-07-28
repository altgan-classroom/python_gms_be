-- migrate:up
DROP PROCEDURE IF EXISTS increase_invoice_and_invoice_item_description_length;
CREATE PROCEDURE increase_invoice_and_invoice_item_description_length()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE invoice
    MODIFY COLUMN description VARCHAR(300);
  ALTER TABLE invoice_item
    MODIFY COLUMN description VARCHAR(300);
END;
CALL increase_invoice_and_invoice_item_description_length();
DROP PROCEDURE increase_invoice_and_invoice_item_description_length;

-- migrate:down
DROP PROCEDURE IF EXISTS revert_invoice_and_invoice_item_description_length;
CREATE PROCEDURE revert_invoice_and_invoice_item_description_length()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE invoice
    MODIFY COLUMN description VARCHAR(100);
  ALTER TABLE invoice_item
    MODIFY COLUMN description VARCHAR(100);
END;
CALL revert_invoice_and_invoice_item_description_length();
DROP PROCEDURE revert_invoice_and_invoice_item_description_length;
