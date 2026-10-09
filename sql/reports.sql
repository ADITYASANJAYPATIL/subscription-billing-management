
-- Subscription & Billing Management System
-- SQL reporting queries
-- Database: PostgreSQL

-- Report 1: Subscription count by status
SELECT
    status,
    COUNT(*) AS subscription_count
FROM subscriptions_subscription
GROUP BY status
ORDER BY status;


-- Report 2: Total successful revenue by subscription plan
-- Only successful payments are included.
SELECT
    sp.id AS plan_id,
    sp.name AS plan_name,
    COALESCE(SUM(p.amount), 0) AS total_revenue
FROM plans_subscriptionplan AS sp
LEFT JOIN subscriptions_subscription AS s
    ON s.plan_id = sp.id
LEFT JOIN billing_payment AS p
    ON p.subscription_id = s.id
    AND p.status = 'SUCCESS'
GROUP BY sp.id, sp.name
ORDER BY sp.name;


-- Report 3: Monthly successful revenue
SELECT
    DATE_TRUNC('month', payment_date)::date AS revenue_month,
    SUM(amount) AS total_revenue
FROM billing_payment
WHERE status = 'SUCCESS'
GROUP BY DATE_TRUNC('month', payment_date)::date
ORDER BY revenue_month;


-- Report 4: Current active subscriptions
SELECT
    s.id AS subscription_id,
    cp.id AS customer_id,
    u.username AS customer_username,
    sp.name AS plan_name,
    sp.price AS plan_price,
    sp.billing_cycle,
    s.start_date,
    s.end_date
FROM subscriptions_subscription AS s
INNER JOIN accounts_customerprofile AS cp
    ON cp.id = s.customer_id
INNER JOIN auth_user AS u
    ON u.id = cp.user_id
INNER JOIN plans_subscriptionplan AS sp
    ON sp.id = s.plan_id
WHERE s.status = 'ACTIVE'
ORDER BY s.start_date DESC;


-- Report 5: Cancelled and expired subscriptions
SELECT
    s.id AS subscription_id,
    cp.id AS customer_id,
    u.username AS customer_username,
    sp.name AS plan_name,
    s.status,
    s.start_date,
    s.end_date
FROM subscriptions_subscription AS s
INNER JOIN accounts_customerprofile AS cp
    ON cp.id = s.customer_id
INNER JOIN auth_user AS u
    ON u.id = cp.user_id
INNER JOIN plans_subscriptionplan AS sp
    ON sp.id = s.plan_id
WHERE s.status IN ('CANCELLED', 'EXPIRED')
ORDER BY s.end_date DESC NULLS LAST;
