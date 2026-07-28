-- migrate:up

DROP PROCEDURE IF EXISTS drop_void_by_fk;
CREATE PROCEDURE drop_void_by_fk()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE invoice DROP FOREIGN KEY invoice_ibfk_8;
END;

CALL drop_void_by_fk();
DROP PROCEDURE drop_void_by_fk;


-- migrate:down

DROP PROCEDURE IF EXISTS add_void_by_fk;
CREATE PROCEDURE add_void_by_fk()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE invoice
    ADD CONSTRAINT invoice_ibfk_8 FOREIGN KEY (void_by) REFERENCES user(id);
END;

CALL add_void_by_fk();
DROP PROCEDURE add_void_by_fk;

