use 외환계좌;
SELECT * FROM 외환계좌.currencies;

-- 데이터 생성
INSERT INTO `외환계좌`.`currencies`(`currency_code`, `currency_name`, `minor_unit`)
VALUES
('KRW', 'Korean Won', 0),
('USD', 'US Dollar', 2),
('JPY', 'Japanese Yen', 0),
('EUR', 'Euro', 2),
('GBP', 'Pound Sterling', 2),
('AUD', 'Australian Dollar', 2);

INSERT INTO `외환계좌`.`users` (`user_id`, `email`, `full_name`, `status`)
VALUES
(1, 'alice@example.com', 'Alice Kim', 1),
(2, 'bob@example.com', 'Bob Lee', 1),
(3, 'carol@example.com', 'Carol Park', 1),
(4, 'dave@example.com', 'Dave Choi', 1),
(5, 'erin@example.com', 'Erin Jung', 0),
(6, 'frank@example.com', 'Frank Yoo', 1),
(7, 'grace@example.com', 'Grace Han', 1),
(8, 'heidi@example.com', 'Heidi Lim', 1);

INSERT INTO `fx_holdings` (`user_id`, `currency_code`, `dalance`, `updated_at`)
VALUES
(1, 'KRW', 1200000.00000000, NOW()),
(1, 'USD', 950.25000000, NOW()),
(1, 'EUR', 210.00000000, NOW()),
(2, 'KRW', 560000.00000000, NOW()),
(2, 'JPY', 75000.00000000, NOW()),
(3, 'USD', 1250.75000000, NOW()),
(3, 'GBP', 80.00000000, NOW()),
(4, 'KRW', 330000.00000000, NOW()),
(4, 'USD', 420.00000000, NOW()),
(4, 'JPY', 12000.00000000, NOW()),
(5, 'EUR', 500.00000000, NOW()),
(5, 'AUD', 600.00000000, NOW()),
(6, 'KRW', 980000.00000000, NOW()),
(6, 'USD', 110.00000000, NOW()),
(6, 'EUR', 45.50000000, NOW()),
(7, 'JPY', 150000.00000000, NOW()),
(7, 'GBP', 30.00000000, NOW()),
(8, 'KRW', 250000.00000000, NOW()),
(8, 'AUD', 120.00000000, NOW());

-- 문제 1
SELECT
    u.user_id,
    u.full_name,
    f.currency_code,
    f.balance
FROM users u
JOIN fx_holdings f
    ON u.user_id = f.user_id
ORDER BY
    u.user_id ASC,
    f.currency_code ASC;
    
-- 문제 2
select f.currency_code, f.balance
from users u 
	join fx_holdings f
    on u.user_id = f.user_id
where email = 'alice@example.com'
order by f.currency_code asc;

-- 문제 3
select currency_code, sum(balance) as total_balance
from fx_holdings
group by currency_code
order by currency_code asc;

-- 문제 4
select u.user_id, u.full_name, count(distinct fx.currency_code) as currency_cnt, sum(fx.balance) as sum_raw
from users u join fx_holdings fx
on u.user_id = fx.user_id
group by u.user_id, u.full_name
order by u.user_id asc;

-- 문제 5
select u.full_name, f.balance
from users u 
	join fx_holdings f
	on u.user_id = f.user_id
where f.currency_code = 'KRW'
order by f.balance desc
limit 5;

-- 문제 6
select u.full_name, f.balance
from fx_holdings f 
	join users u
    on u.user_id = f.user_id
where f.currency_code = 'USD'
order by f.balance desc;

-- 문제 7
select u.user_id, u.full_name, count(distinct f.currency_code)
from users u 
	join fx_holdings f
    on u.user_id = f.user_id
group by u.user_id, u.full_name
having count(distinct f.currency_code) >= '2'
order by count(distinct f.currency_code) desc, u.full_name asc;

-- 문제 8
select u.full_name, f.currency_code, f.balance
from users u 
	join fx_holdings f 
    on u.user_id = f.user_id
where u.status = 0

-- 문제 9
USE `외환계좌`;
select c.currency_name, c.currency_code, f.balance
from fx_holdings f
	join users u
    on f.user_id = u.user_id
	join currencies c
    on f.currency_code = c.currency_code
where u.email = "alice@example.com"
order by c.currency_code asc;

-- 문제 10
select currency_code, count(distinct holding_id) as holder_count, sum(balance) as total_balance 
from fx_holdings 
group by currency_code
order by currency_code asc;

-- end!!! :) :) 