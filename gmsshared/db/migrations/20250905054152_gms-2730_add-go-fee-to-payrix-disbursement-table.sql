-- migrate:up

DROP PROCEDURE IF EXISTS add_go_fee_to_payrix_disbursement_table;
CREATE PROCEDURE add_go_fee_to_payrix_disbursement_table()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE payrix_disbursement ADD COLUMN go_fees float DEFAULT 0;
END;
CALL add_go_fee_to_payrix_disbursement_table();
DROP PROCEDURE add_go_fee_to_payrix_disbursement_table;


-- migrate:down

DROP PROCEDURE IF EXISTS drop_go_fee_to_payrix_disbursement_table;
CREATE PROCEDURE drop_go_fee_to_payrix_disbursement_table()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE payrix_disbursement DROP COLUMN go_fees;
END;
CALL drop_go_fee_to_payrix_disbursement_table();
DROP PROCEDURE drop_go_fee_to_payrix_disbursement_table;
