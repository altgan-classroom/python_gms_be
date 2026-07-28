-- migrate:up

DROP PROCEDURE IF EXISTS add_fee_columns_to_payment_history_tables;
CREATE PROCEDURE add_fee_columns_to_payment_history_tables()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE member_payment_history ADD COLUMN revenue_share_fee float NOT NULL DEFAULT '0';
  ALTER TABLE member_payment_history ADD COLUMN payrix_disbursement_id varchar(50) DEFAULT NULL;
  ALTER TABLE member_payment_history_v2 ADD COLUMN revenue_share_fee FLOAT NULL DEFAULT 0;
  ALTER TABLE member_payment_history_v2 ADD COLUMN payrix_disbursement_id varchar(50) DEFAULT NULL;
END;
CALL add_fee_columns_to_payment_history_tables();
DROP PROCEDURE add_fee_columns_to_payment_history_tables;


-- migrate:down

DROP PROCEDURE IF EXISTS drop_fee_columns_to_payment_history_tables;
CREATE PROCEDURE drop_fee_columns_to_payment_history_tables()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE member_payment_history DROP COLUMN revenue_share_fee;
  ALTER TABLE member_payment_history DROP COLUMN payrix_disbursement_id;
  ALTER TABLE member_payment_history_v2 DROP COLUMN revenue_share_fee;
  ALTER TABLE member_payment_history_v2 DROP COLUMN payrix_disbursement_id;
END;
CALL drop_fee_columns_to_payment_history_tables();
DROP PROCEDURE drop_fee_columns_to_payment_history_tables;
