-- migrate:up

UPDATE report
SET name = 'Payments', description = 'Payments'
WHERE name = 'Net Income';

-- migrate:down

UPDATE report
SET name = 'Net Income', description = 'Net Income'
WHERE name = 'Payments';
