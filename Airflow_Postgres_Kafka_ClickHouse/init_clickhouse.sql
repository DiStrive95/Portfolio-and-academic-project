CREATE TABLE IF NOT EXISTS users_analytics (
    event_date Date,
    role String,
    unique_users AggregateFunction(uniq, UInt32),
    total_actions AggregateFunction(count, UInt32)
) ENGINE = AggregatingMergeTree
ORDER BY (event_date, role);