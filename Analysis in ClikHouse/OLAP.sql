CREATE TABLE user_events (
user_id UInt32,
event_type String,
points_spent UInt32,
event_time DateTime
) ENGINE = MergeTree
ORDER BY (event_time, user_id)
TTL event_time + INTERVAL 30 DAY DELETE;


CREATE TABLE user_event_agg (
event_type String,
event_date Date,
unique_users AggregateFunction(uniq, UInt32),
sum_point AggregateFunction(sum, UInt32),
count_action AggregateFunction(count, UInt32)
) ENGINE = AggregatingMergeTree
ORDER BY (event_date, event_type)
TTL event_date + INTERVAL 180 DAY DELETE;


CREATE MATERIALIZED VIEW user_event_mv
TO user_event_agg
AS
SELECT
    event_type,
    CAST(event_time AS Date) AS event_date,
    uniqState(user_id) AS unique_users,
    sumState(points_spent) AS sum_point,
    countState() AS count_action
FROM user_events
GROUP BY event_type, event_date
ORDER BY (event_type, event_date);

INSERT INTO user_events VALUES
(1, 'login', 0, now() - INTERVAL 10 DAY),
(2, 'signup', 0, now() - INTERVAL 10 DAY),
(3, 'login', 0, now() - INTERVAL 10 DAY),

(1, 'login', 0, now() - INTERVAL 7 DAY),
(2, 'login', 0, now() - INTERVAL 7 DAY),
(3, 'purchase', 30, now() - INTERVAL 7 DAY),

(1, 'purchase', 50, now() - INTERVAL 5 DAY),
(2, 'logout', 0, now() - INTERVAL 5 DAY),
(4, 'login', 0, now() - INTERVAL 5 DAY),

(1, 'login', 0, now() - INTERVAL 3 DAY),
(3, 'purchase', 70, now() - INTERVAL 3 DAY),
(5, 'signup', 0, now() - INTERVAL 3 DAY),

(2, 'purchase', 20, now() - INTERVAL 1 DAY),
(4, 'logout', 0, now() - INTERVAL 1 DAY),
(5, 'login', 0, now() - INTERVAL 1 DAY),

(1, 'purchase', 25, now()),
(2, 'login', 0, now()),
(3, 'logout', 0, now()),
(6, 'signup', 0, now()),
(6, 'purchase', 100, now());


WITH first_visit AS (
    SELECT
        user_id,
        CAST(min(event_time) AS Date) AS first_visit_date
    FROM user_events
    GROUP BY user_id
),

retention AS (
    SELECT
        first_visit_date,
        count(DISTINCT fv.user_id) as total_users_day_0,
        countIf(DISTINCT ue.user_id, CAST(ue.event_time AS DATE) BETWEEN first_visit_date + 1 AND first_visit_date + 7) as returned_in_7_days  --хотелось использовать CASE или FILTER
    FROM first_visit fv
    LEFT JOIN user_events ue ON fv.user_id = ue.user_id
    GROUP BY first_visit_date
)
SELECT
    total_users_day_0,
    returned_in_7_days,
    round(returned_in_7_days * 100.0 / total_users_day_0, 2) as retention_7d_percent
FROM retention
ORDER BY first_visit_date;


SELECT
    event_date,
    event_type,
    uniqMerge(unique_users) as unique_users,
    sumMerge(sum_point) as total_spend,
    countMerge(count_action) as total_actions
FROM user_event_agg
GROUP BY event_date, event_type
ORDER BY event_date, event_type;