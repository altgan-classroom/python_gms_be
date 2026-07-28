-- migrate:up

DROP PROCEDURE IF EXISTS add_fee_columns_to_revenue_share_table;
CREATE PROCEDURE add_fee_columns_to_revenue_share_table()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE _ref_revenue_share ADD COLUMN percentage FLOAT NULL DEFAULT 0;
  ALTER TABLE _ref_revenue_share ADD COLUMN fee_id varchar(50) NULL;
END;
CALL add_fee_columns_to_revenue_share_table();
DROP PROCEDURE add_fee_columns_to_revenue_share_table;


-- migrate:down

DROP PROCEDURE IF EXISTS drop_fee_columns_to_revenue_share_table;
CREATE PROCEDURE drop_fee_columns_to_revenue_share_table()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE _ref_revenue_share DROP COLUMN percentage;
  ALTER TABLE _ref_revenue_share DROP COLUMN fee_id;
END;
CALL drop_fee_columns_to_revenue_share_table();
DROP PROCEDURE drop_fee_columns_to_revenue_share_table;
