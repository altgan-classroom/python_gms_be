-- migrate:up
CREATE TABLE class_access_group (
    id BIGINT PRIMARY KEY auto_increment,
    location_id BIGINT NOT NULL,
    name VARCHAR(50) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    create_datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES location(id)
);

CREATE TABLE class_access_group_plan (
    class_access_group_id BIGINT NOT NULL,
    plan_id BIGINT NOT NULL,
    FOREIGN KEY (class_access_group_id) REFERENCES class_access_group(id),
    FOREIGN KEY (plan_id) REFERENCES plan(id)
);

CREATE TABLE class_access_group_class(
    class_access_group_id BIGINT NOT NULL,
    class_id BIGINT NOT NULL,
    FOREIGN KEY (class_access_group_id) REFERENCES class_access_group(id),
    FOREIGN KEY (class_id) REFERENCES class(id)
);

CREATE TABLE class_access_group_format(
    class_access_group_id BIGINT NOT NULL,
    plan_type_id INT NOT NULL,
    FOREIGN KEY (class_access_group_id) REFERENCES class_access_group(id),
    FOREIGN KEY (plan_type_id) REFERENCES _ref_plan_type(id)
);

ALTER TABLE location ADD COLUMN class_access_group BOOLEAN NOT NULL DEFAULT FALSE;


-- migrate:down

