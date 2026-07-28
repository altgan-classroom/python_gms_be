-- migrate:up

CREATE TABLE `_ref_door_access_vendor`
(
    `id`              int         NOT NULL AUTO_INCREMENT,
    `name`            varchar(30) NOT NULL,
    `description`     varchar(200)  NULL,
    `authentication_type`  varchar(50) NOT NULL,
    `api_url`         varchar(200) NOT NULL,
    `create_datetime` datetime    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_datetime` datetime    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
);

CREATE TABLE `_ref_door_access_vendor_auth`
(
    `id`              int         NOT NULL AUTO_INCREMENT,
    `vendor_id`       int NOT NULL,
    `display_name`    varchar(100) NULL,
    `field_name`      varchar(50) NOT NULL,
    `field_type`      varchar(50) NOT NULL,
    `field_validation_rules_json` JSON NULL,
    `field_help_text` varchar(200) NULL,
    `create_datetime` datetime    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_datetime` datetime    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `vendor_id` (`vendor_id`),
    CONSTRAINT `_ref_door_access_vendor_auth_ibfk_1` FOREIGN KEY (`vendor_id`) REFERENCES `_ref_door_access_vendor` (`id`)
);

CREATE TABLE `door_access_location_auth`
(
    `id`              int         NOT NULL AUTO_INCREMENT,
    `location_id`     bigint      NOT NULL,
    `field_id`        int         NOT NULL,
    `field_value`     varchar(100) NOT NULL,
    `create_datetime` datetime    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_datetime` datetime    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `location_id` (`location_id`),
    KEY `field_id` (`field_id`),
    CONSTRAINT `door_access_location_auth_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
    CONSTRAINT `door_access_location_auth_ibfk_2` FOREIGN KEY (`field_id`) REFERENCES `_ref_door_access_vendor_auth` (`id`)
);

create table door_access_log
(
    id                   bigint auto_increment,
    resource             int                                not null,
    resource_id          varchar(50)                        null,
    request_type         varchar(10)                        null,
    request_url          varchar(250)                       not null,
    request_datetime     datetime default CURRENT_TIMESTAMP not null,
    request_payload      json                               null,
    response_payload     json                               null,
    response_datetime    datetime default CURRENT_TIMESTAMP not null,
    response_status_code int                                null,
    error                varchar(1000)                      null,
    location_id          bigint                             null,
    user_id              bigint                             null,
    door_id              bigint                             null,
    group_id             bigint                             null,
    PRIMARY KEY (`id`)
);

DROP PROCEDURE IF EXISTS add_columns_to_location;
CREATE PROCEDURE add_columns_to_location()
BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
  ALTER TABLE location ADD COLUMN door_access BOOLEAN NULL DEFAULT 0;
  ALTER TABLE location ADD COLUMN door_access_auth_status int NOT NULL DEFAULT '0';
  ALTER TABLE location ADD COLUMN door_access_auth_error JSON null;
  ALTER TABLE location ADD COLUMN door_access_vendor_id int null;
  ALTER TABLE location ADD CONSTRAINT location_ibfk_8 FOREIGN KEY (door_access_vendor_id) REFERENCES _ref_door_access_vendor (id);
END;
CALL add_columns_to_location();
DROP PROCEDURE add_columns_to_location;


INSERT INTO _ref_door_access_vendor (name, description, authentication_type, api_url)
values ('Kisi', '', 'api_key', 'https://api.kisi.io');

INSERT INTO _ref_door_access_vendor_auth (vendor_id, display_name, field_name, field_type, field_validation_rules_json, field_help_text)
values ((select id from _ref_door_access_vendor where name = 'Kisi'), 'API KEY', 'api_key', 'textbox', '{"minLength": 32, "maxLength": 32, "required": true}', 'API KEY to use Kisi API');
-- migrate:down

