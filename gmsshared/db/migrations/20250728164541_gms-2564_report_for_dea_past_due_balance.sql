-- migrate:up
DROP PROCEDURE IF EXISTS add_quicksight_past_due_balance_report;
CREATE PROCEDURE add_quicksight_past_due_balance_report()
BEGIN
    -- Declare some stored procedure variables
    DECLARE report_name CHAR(50) DEFAULT 'Past Due Balance';
    DECLARE test_dashboard_id CHAR(50) DEFAULT '0258cf84-e08a-483d-b953-d90eb7ba5f1b';
    DECLARE prod_dashboard_id CHAR(50) DEFAULT 'cd3b6b91-f1d8-4041-b350-823ef004fa9e';
    DECLARE stage_dashboard_id CHAR(50) DEFAULT '9c69a908-bce4-409f-884e-2a350bcf389b';

    -- Declare an exit handler to rollback on any error
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    -- Start transaction
    START TRANSACTION;

    INSERT INTO `report` (name, description, dashboard_id, sheet_id, visual_id, environment, active)
    VALUES  (report_name, report_name, test_dashboard_id,'', '', 'test', 1),
            (report_name, report_name, prod_dashboard_id,'', '', 'prod', 1),
            (report_name, report_name, stage_dashboard_id,'', '', 'stage', 1);

    -- Insert into report_role table
    INSERT INTO report_role (report_role.report_id, report_role.role_type_id)
    SELECT report.id AS report_id, _ref_role_type.id AS role_type_id
    FROM report
    JOIN _ref_role_type ON _ref_role_type.name IN ('Owner', 'Manager')
    WHERE report.name = report_name
      AND report.environment IN ('test', 'prod', 'stage');

    -- Commit transaction if all succeeded
    COMMIT;
END;
CALL add_quicksight_past_due_balance_report();
DROP PROCEDURE add_quicksight_past_due_balance_report;


-- migrate:down
DROP PROCEDURE IF EXISTS remove_quicksight_past_due_balance_report;
CREATE PROCEDURE remove_quicksight_past_due_balance_report()
BEGIN
    -- Declare the report name
    DECLARE report_name CHAR(50) DEFAULT 'Past Due Balance';

    -- Declare an exception handler
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;

    -- Remove from report_role first to avoid FK constraint issues
    DELETE FROM report_role
    WHERE report_role.report_id IN (
        SELECT report.id FROM report
        WHERE report.name = report_name
        AND report.environment IN ('test', 'prod', 'stage')
    );

    -- Remove from report
    DELETE FROM report
    WHERE report.name = report_name;
END;
CALL remove_quicksight_past_due_balance_report();
DROP PROCEDURE remove_quicksight_past_due_balance_report;
