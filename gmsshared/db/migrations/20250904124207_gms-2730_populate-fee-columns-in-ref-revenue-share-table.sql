-- migrate:up

-- Update each record individually for better clarity and transaction safety
UPDATE _ref_revenue_share SET payrix_fee_ids = '["p1_fee_66cd19b0d2d016b0500b7d4", "p1_fee_66cd1937288879ec76a4f86"]', revenue_share_fee = 11.41 WHERE id = 15;
UPDATE _ref_revenue_share SET payrix_fee_ids = '["p1_fee_66cd1ba9eb1628dc5feb883", "p1_fee_66cd1b4a43b6a8210d90f5b"]', revenue_share_fee = 8.41 WHERE id = 16;
UPDATE _ref_revenue_share SET payrix_fee_ids = '["p1_fee_66cdc62ee43803982ccbb93", "p1_fee_66cdc5efbfba368d3369a69"]', revenue_share_fee = 6.41 WHERE id = 17;
UPDATE _ref_revenue_share SET payrix_fee_ids = '["p1_fee_66cdc793d9b4cb160ca1e52", "p1_fee_66cdc737acd10e2d5e93e7d"]', revenue_share_fee = 5.41 WHERE id = 18;
UPDATE _ref_revenue_share SET payrix_fee_ids = '["p1_fee_66cdc8eaad14d0c0851012c", "p1_fee_66cdc8a5a2249acfc74e7e9"]', revenue_share_fee = 15.41 WHERE id = 19;
UPDATE _ref_revenue_share SET payrix_fee_ids = '["p1_fee_66cdcd8eb1f2b57dea960f4", "p1_fee_66cdcd43037eb4aa0f60f00"]', revenue_share_fee = 9.91 WHERE id = 20;
UPDATE _ref_revenue_share SET payrix_fee_ids = '["p1_fee_66cdceaaf3e93da096ebcfd", "p1_fee_66cdce64b6e28e283f48925"]', revenue_share_fee = 7.41 WHERE id = 21;
UPDATE _ref_revenue_share SET payrix_fee_ids = '["p1_fee_66cdd00d852eac57a4c5895", "p1_fee_66cdcfcfbc1a8e4267a5847"]', revenue_share_fee = 6.41 WHERE id = 22;
UPDATE _ref_revenue_share SET payrix_fee_ids = '["p1_fee_675dd51a6763cd652a63590", "p1_fee_675dd56ebf4d058571ed3ae"]', revenue_share_fee = 16.41 WHERE id = 23;
UPDATE _ref_revenue_share SET payrix_fee_ids = '["p1_fee_675dd68dbbf45976ebe1733", "p1_fee_675dd6c78b3c96e58a09e4a"]', revenue_share_fee = 11.41 WHERE id = 24;
UPDATE _ref_revenue_share SET payrix_fee_ids = '["p1_fee_675dd7b3c20990474d00dbe", "p1_fee_675dd82ecab867217ba4288"]', revenue_share_fee = 5.41 WHERE id = 25;
UPDATE _ref_revenue_share SET payrix_fee_ids = '["p1_fee_675dd92b94f83f6416d9f53", "p1_fee_675dd9b83dd2b71318ae16b"]', revenue_share_fee = 2.41 WHERE id = 26;
UPDATE _ref_revenue_share SET payrix_fee_ids = '["p1_fee_65b9229a25537102ec27f22", "p1_fee_65b920cebd36fd6f270d5e1"]', revenue_share_fee = 1.42 WHERE id = 27;
UPDATE _ref_revenue_share SET payrix_fee_ids = NULL, revenue_share_fee = NULL WHERE id = 28;
UPDATE _ref_revenue_share SET payrix_fee_ids = '["p1_fee_674733bb75e0a9406db1df1", "p1_fee_67450535b744cac1d7b37b6"]', revenue_share_fee = 1.82 WHERE id = 29;
UPDATE _ref_revenue_share SET payrix_fee_ids = '["p1_fee_67532fff6cf60508be10085", "p1_fee_67533096a96c213ed2e146d"]', revenue_share_fee = 9.42 WHERE id = 30;

-- migrate:down

-- Revert each update individually
UPDATE _ref_revenue_share SET payrix_fee_ids = NULL, revenue_share_fee = 0 WHERE id IN (15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30);
