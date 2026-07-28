-- migrate:up

CREATE TABLE `_ref_payrix_payment_method_type`
(
    `id`              int         NOT NULL AUTO_INCREMENT,
    `name`            varchar(30) NOT NULL,
    `description`     varchar(200)         DEFAULT NULL,
    `create_datetime` datetime    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_datetime` datetime    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
);

INSERT INTO `_ref_payrix_payment_method_type` VALUES (1,'Amex','Amercian Express','2025-07-27 02:51:13','2025-07-27 02:51:13');
INSERT INTO `_ref_payrix_payment_method_type` VALUES (2,'Visa','Visa','2025-07-27 02:51:13','2025-07-27 02:51:13');
INSERT INTO `_ref_payrix_payment_method_type` VALUES (3,'MasterCard','MasterCard','2025-07-27 02:12:34','2025-07-27 02:12:34');
INSERT INTO `_ref_payrix_payment_method_type` VALUES (4,'Diners','Diners Club','2025-07-27 02:12:34','2025-07-27 02:12:34');
INSERT INTO `_ref_payrix_payment_method_type` VALUES (5,'Discover','Discover','2025-07-27 02:12:34','2025-07-27 02:12:34');
INSERT INTO `_ref_payrix_payment_method_type` VALUES (7,'ACH','Checking Account','2025-07-27 02:12:34','2025-07-27 02:12:34');
INSERT INTO `_ref_payrix_payment_method_type` VALUES (8,'ACH','Savings Account','2025-07-27 02:12:34','2025-07-27 02:12:34');
INSERT INTO `_ref_payrix_payment_method_type` VALUES (9,'ACH','Corporate Checking Account','2025-07-27 02:12:34','2025-07-27 02:12:34');
INSERT INTO `_ref_payrix_payment_method_type` VALUES (10,'ACH','Corporate Savings Account','2025-07-27 02:12:34','2025-07-27 02:12:34');

-- migrate:down

