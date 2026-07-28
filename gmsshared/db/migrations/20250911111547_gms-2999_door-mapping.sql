-- migrate:up
CREATE TABLE `door_access_door`
(
    `id`              bigint       NOT NULL AUTO_INCREMENT,
    `location_id`     bigint       NOT NULL,
    `name`            varchar(30)  NOT NULL,
    `door_location`        varchar(50)  DEFAULT NULL,
    `active`     boolean      NOT NULL DEFAULT TRUE,
    `door_onboarding_status_type_id` int  NOT NULL,
    `vendor_door_id` bigint,
    `create_datetime` datetime     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_datetime` datetime     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `location_id` (`location_id`),
    CONSTRAINT `door_access_door_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`)
);

ALTER TABLE location add column door_access_place_id bigint;

-- migrate:down

