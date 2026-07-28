-- migrate:up

CREATE TABLE `_ref_payrix_transaction_error_mapping`
(
    `id`              int           NOT NULL AUTO_INCREMENT,
    `error`           varchar(300)  NOT NULL,
    `decline`         varchar(10)   DEFAULT NULL,
    `create_datetime` datetime      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_datetime` datetime      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
);

INSERT INTO `_ref_payrix_transaction_error_mapping` VALUES
    (1, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Invalid unauth transaction'', ''errorCode'': ''invalid_reverse_auth''}', 'Hard', NOW(), NOW()),
    (2, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Address was not provided, please reattempt transaction.'', ''errorCode'': ''generic_decline''}', 'Hard', NOW(), NOW()),
    (3, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Expired Card'', ''errorCode'': ''expired_card''}', 'Hard', NOW(), NOW()),
    (4, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Closed Account'', ''errorCode'': ''closed_account''}', 'Hard', NOW(), NOW()),
    (5, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Insufficient Funds'', ''errorCode'': ''nsf''}', 'Soft', NOW(), NOW()),
    (6, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Generic Authorization Decline'', ''errorCode'': ''generic_decline''}', 'Hard', NOW(), NOW()),
    (7, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': "Transaction declined: No ''To'' Account Specified", ''errorCode'': ''missing_to_account''}', 'Hard', NOW(), NOW()),
    (8, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Pick Up Card - Stolen'', ''errorCode'': ''stolen_card''}', 'Hard', NOW(), NOW()),
    (9, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Restricted Card'', ''errorCode'': ''restricted_card''}', 'Hard', NOW(), NOW()),
    (10, '{''field'': ''address1'', ''code'': 15, ''severity'': 2, ''msg'': ''Address mismatch, please reattempt transaction.'', ''errorCode'': ''generic_decline''}', 'Hard', NOW(), NOW()),
    (11, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Re-try Transaction'', ''errorCode'': ''reenter_transaction''}', 'Soft', NOW(), NOW()),
    (12, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Pick Up Card, Special Conditions'', ''errorCode'': ''pickup_card''}', 'Hard', NOW(), NOW()),
    (13, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Issuer or Switch Inoperative (MasterCard)'', ''errorCode'': ''issuer_not_available''}', 'Hard', NOW(), NOW()),
    (14, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Suspected Fraud'', ''errorCode'': ''fraudulent''}', 'Hard', NOW(), NOW()),
    (15, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Transaction not Permitted to Cardholder'', ''errorCode'': ''transaction_not_allowed''}', 'Hard', NOW(), NOW()),
    (16, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Invalid CVV'', ''errorCode'': ''invalid_cvv''}', 'Hard', NOW(), NOW()),
    (17, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Invalid Account Number'', ''errorCode'': ''invalid_account''}', 'Hard', NOW(), NOW()),
    (18, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Invalid Transaction'', ''errorCode'': ''transaction_not_allowed''}', 'Soft', NOW(), NOW()),
    (19, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Pick Up Card - Lost'', ''errorCode'': ''lost_card''}', 'Hard', NOW(), NOW()),
    (20, '{''field'': ''total'', ''code'': 15, ''severity'': 2, ''msg'': ''This field only accepts integers between 0 and 9000000000'', ''errorCode'': ''invalid_range''}', 'Hard', NOW(), NOW()),
    (21, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''E-check processing disabled for this account'', ''errorCode'': ''account_return_error''}', 'Hard', NOW(), NOW()),
    (22, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Exceeds Withdrawal Limit'', ''errorCode'': ''withdrawal_limit_exceeded''}', 'Soft', NOW(), NOW()),
    (23, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Invalid refund transaction'', ''errorCode'': ''invalid_refund''}', 'Soft', NOW(), NOW()),
    (24, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Invalid Transaction, Contact Issuer. Card Already Active (Gift Card)'', ''errorCode'': ''card_already_active''}', 'Soft', NOW(), NOW()),
    (25, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Refer to Card Issuer'', ''errorCode'': ''call_issuer''}', 'Soft', NOW(), NOW()),
    (26, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Pick Up Card'', ''errorCode'': ''pickup_card''}', 'Hard', NOW(), NOW()),
    (27, '{''field'': ''fundingCurrency'', ''code'': 15, ''severity'': 2, ''msg'': ''No mid available for txn funding currency'', ''errorCode'': ''funding_currency_error''}', 'Hard', NOW(), NOW()),
    (28, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Exceeds Withdrawal Frequency Limit'', ''errorCode'': ''withdrawal_count_limit_exceeded''}', 'Soft', NOW(), NOW()),
    (29, '{''field'': ''total'', ''code'': 15, ''severity'': 2, ''msg'': ''Transaction total exceeds upper limit'', ''errorCode'': ''txn_limit_exceeded''}', 'Soft', NOW(), NOW()),
    (30, '{''field'': None, ''code'': 15, ''severity'': 2, ''msg'': ''Transaction declined: Allowable Number of PIN Tries Exceeded'', ''errorCode'': ''pin_try_exceeded''}', 'Soft', NOW(), NOW()),
    (31, '{''code'': 15, ''severity'': 3, ''msg'': ''The related merchants record is inactive'', ''errorCode'': ''record_change_disabled''}', 'Hard', NOW(), NOW()),
    (32, '{"code":15,"severity":2,"field":null,"msg":"Address was not provided, please reattempt transaction.","errorCode":"generic_decline"}', 'Hard', NOW(), NOW()),
    (33, '{"code":15,"severity":2,"field":"address1","msg":"Address was not provided, please reattempt transaction.","errorCode":"generic_decline"}', 'Hard', NOW(), NOW()),
    (34, '{"code":15,"severity":2,"field":"payment.cvv","msg":"Card Verification (CVV) was not provided, please reattempt transaction.","errorCode":"generic_decline"}', 'Hard', NOW(), NOW()),
    (35, '{"code":15,"severity":2,"field":null,"msg":"Transaction declined: Suspected Fraud","errorCode":"fraudulent"}', 'Hard', NOW(), NOW());


-- migrate:down

DROP TABLE `_ref_payrix_transaction_error_mapping`;
