-- migrate:up

ALTER TABLE _ref_revenue_share
CHANGE COLUMN percentage revenue_share_fee FLOAT NULL DEFAULT 0,
CHANGE COLUMN fee_id payrix_fee_ids JSON NULL;


-- migrate:down

ALTER TABLE _ref_revenue_share
CHANGE COLUMN revenue_share_fee percentage FLOAT NULL DEFAULT 0,
CHANGE COLUMN payrix_fee_ids fee_id VARCHAR(50) NULL;
