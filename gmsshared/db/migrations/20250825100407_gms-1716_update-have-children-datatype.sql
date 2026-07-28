-- migrate:up
DROP PROCEDURE IF EXISTS change_have_children_to_boolean;
CREATE PROCEDURE change_have_children_to_boolean()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;

  UPDATE user_profile
  SET have_children = CASE
    WHEN UPPER(have_children) = 'Y' THEN '1'
    WHEN UPPER(have_children) = 'N' THEN '0'
    ELSE have_children
  END;

  ALTER TABLE user_profile
    MODIFY COLUMN have_children BOOLEAN;
END;
CALL change_have_children_to_boolean();
DROP PROCEDURE change_have_children_to_boolean;

-- migrate:down
DROP PROCEDURE IF EXISTS change_have_children_to_varchar;
CREATE PROCEDURE change_have_children_to_varchar()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;

  ALTER TABLE user_profile
    MODIFY COLUMN have_children VARCHAR(10);

  UPDATE user_profile
  SET have_children = CASE
    WHEN have_children = '1' OR have_children = 'true' THEN 'Y'
    WHEN have_children = '0' OR have_children = 'false' THEN 'N'
    ELSE have_children
  END;
END;
CALL change_have_children_to_varchar();
DROP PROCEDURE change_have_children_to_varchar;