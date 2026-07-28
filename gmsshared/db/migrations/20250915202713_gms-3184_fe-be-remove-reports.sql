-- migrate:up
DROP PROCEDURE IF EXISTS remove_deprecated_quicksight_reports;
CREATE PROCEDURE remove_deprecated_quicksight_reports()
BEGIN
    -- Declare report names to remove
    DECLARE report_name1 CHAR(50) DEFAULT 'New Memberships Sales';
    DECLARE report_name2 CHAR(50) DEFAULT 'Active Contacts without a Payment Method';
    DECLARE report_name3 CHAR(50) DEFAULT 'Balance & Future Contract Value';
    DECLARE report_name4 CHAR(50) DEFAULT 'Outstanding Balance';

    -- Declare an exit handler to rollback on any error
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    -- Start transaction
    START TRANSACTION;

    -- Remove from report_role first to avoid FK constraint issues
    DELETE rr FROM report_role rr
    JOIN report r ON rr.report_id = r.id
    WHERE r.name IN (report_name1, report_name2, report_name3, report_name4)
      AND r.environment IN ('test', 'prod', 'stage');

    -- Remove from report
    DELETE FROM report
    WHERE name IN (report_name1, report_name2, report_name3, report_name4)
      AND environment IN ('test', 'prod', 'stage');

    -- Commit transaction if all succeeded
    COMMIT;
END;
CALL remove_deprecated_quicksight_reports();
DROP PROCEDURE remove_deprecated_quicksight_reports;


-- migrate:down
DROP PROCEDURE IF EXISTS restore_deprecated_quicksight_reports;
CREATE PROCEDURE restore_deprecated_quicksight_reports()
BEGIN
    -- Declare report names and their details
    DECLARE report_name1 CHAR(50) DEFAULT 'New Memberships Sales';
    DECLARE report_name2 CHAR(50) DEFAULT 'Active Contacts without a Payment Method';
    DECLARE report_name3 CHAR(50) DEFAULT 'Balance & Future Contract Value';
    DECLARE report_name4 CHAR(50) DEFAULT 'Outstanding Balance';

    -- Dashboard IDs for each report and environment
    DECLARE new_memberships_test CHAR(50) DEFAULT 'e0b15295-e1d6-4c43-9548-5cd5c87ca4f6';
    DECLARE new_memberships_prod CHAR(50) DEFAULT '2692d910-b812-475f-924f-39e676df31d3';
    DECLARE new_memberships_stage CHAR(50) DEFAULT '2692d910-b812-475f-924f-39e676df31d3';

    DECLARE active_contacts_test CHAR(50) DEFAULT '4beea0b8-3ab7-4f2a-b36c-9e495589fbc5';
    DECLARE active_contacts_prod CHAR(50) DEFAULT 'e83aeb50-3d42-451e-89db-f8fe479c7d68';
    DECLARE active_contacts_stage CHAR(50) DEFAULT 'e83aeb50-3d42-451e-89db-f8fe479c7d68';

    DECLARE balance_future_test CHAR(50) DEFAULT '319a21fa-cc50-4213-acc2-cebab2c5934a';
    DECLARE balance_future_prod CHAR(50) DEFAULT '7cb04818-6d42-4689-84c2-0b2a08e78bbe';
    DECLARE balance_future_stage CHAR(50) DEFAULT '7cb04818-6d42-4689-84c2-0b2a08e78bbe';

    DECLARE outstanding_balance_test CHAR(50) DEFAULT 'f064ea71-6cd1-4fc1-b190-31bfdda5ab1c';
    DECLARE outstanding_balance_prod CHAR(50) DEFAULT 'db4cf55d-e341-43e2-a56e-cd314efed683';
    DECLARE outstanding_balance_stage CHAR(50) DEFAULT 'db4cf55d-e341-43e2-a56e-cd314efed683';

    -- Declare an exit handler to rollback on any error
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    -- Start transaction
    START TRANSACTION;

    -- Insert reports back into the report table
    INSERT INTO `report` (name, description, dashboard_id, sheet_id, visual_id, environment, active)
    VALUES
        -- New Memberships Sales
        (report_name1, report_name1, new_memberships_test, '', '', 'test', 1),
        (report_name1, report_name1, new_memberships_prod, '', '', 'prod', 1),
        (report_name1, report_name1, new_memberships_stage, '', '', 'stage', 1),

        -- Active Contacts without a Payment Method
        (report_name2, report_name2, active_contacts_test, '', '', 'test', 1),
        (report_name2, report_name2, active_contacts_prod, '', '', 'prod', 1),
        (report_name2, report_name2, active_contacts_stage, '', '', 'stage', 1),

        -- Balance & Future Contract Value
        (report_name3, report_name3, balance_future_test, '', '', 'test', 1),
        (report_name3, report_name3, balance_future_prod, '', '', 'prod', 1),
        (report_name3, report_name3, balance_future_stage, '', '', 'stage', 1),

        -- Outstanding Balance
        (report_name4, report_name4, outstanding_balance_test, '', '', 'test', 1),
        (report_name4, report_name4, outstanding_balance_prod, '', '', 'prod', 1),
        (report_name4, report_name4, outstanding_balance_stage, '', '', 'stage', 1);

    -- Insert into report_role table for each report
    -- New Memberships Sales (Owner=1, Manager=4)
    INSERT INTO report_role (report_id, role_type_id)
    SELECT r.id AS report_id, rt.id AS role_type_id
    FROM report r
    CROSS JOIN (SELECT id FROM _ref_role_type WHERE name IN ('Owner', 'Manager')) rt
    WHERE r.name = report_name1
      AND r.environment IN ('test', 'prod', 'stage');

    -- Active Contacts without a Payment Method (Owner=1, Manager=4, Admin=3, Support=5)
    INSERT INTO report_role (report_id, role_type_id)
    SELECT r.id AS report_id, rt.id AS role_type_id
    FROM report r
    CROSS JOIN (SELECT id FROM _ref_role_type WHERE name IN ('Owner', 'Manager', 'Admin', 'Support')) rt
    WHERE r.name = report_name2
      AND r.environment IN ('test', 'prod', 'stage');

    -- Balance & Future Contract Value (Owner=1, Manager=4)
    INSERT INTO report_role (report_id, role_type_id)
    SELECT r.id AS report_id, rt.id AS role_type_id
    FROM report r
    CROSS JOIN (SELECT id FROM _ref_role_type WHERE name IN ('Owner', 'Manager')) rt
    WHERE r.name = report_name3
      AND r.environment IN ('test', 'prod', 'stage');

    -- Outstanding Balance (Owner=1, Manager=4)
    INSERT INTO report_role (report_id, role_type_id)
    SELECT r.id AS report_id, rt.id AS role_type_id
    FROM report r
    CROSS JOIN (SELECT id FROM _ref_role_type WHERE name IN ('Owner', 'Manager')) rt
    WHERE r.name = report_name4
      AND r.environment IN ('test', 'prod', 'stage');

    -- Commit transaction if all succeeded
    COMMIT;
END;
CALL restore_deprecated_quicksight_reports();
DROP PROCEDURE restore_deprecated_quicksight_reports;
