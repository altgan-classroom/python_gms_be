-- migrate:up
CREATE TABLE `door_access_updates_log`
(
    `id`              bigint       NOT NULL AUTO_INCREMENT,
    `vendor_id`       int          NOT NULL,
    `vendor_location_id`     varchar(50)       NULL,
    `actor_id`        varchar(50) NULL,
    `event_id`        varchar(50) NULL,
    `event_type`      int NULL,
    `error_code`      varchar(15) NULL,
    `event_payload`   json null,
    `create_datetime` datetime     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_datetime` datetime     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
);

-- migrate:down

