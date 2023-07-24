CREATE TABLE default.klines
(
    `symbol` String,
    `openTime` DateTime,
    `closeTime` DateTime64(3),
    `openPrice` Float64,
    `highPrice` Float64,
    `lowPrice` Float64,
    `closePrice` Float64,
    `volume` Float64
)
ENGINE = ReplacingMergeTree
PRIMARY KEY (symbol, openTime)
ORDER BY (symbol, openTime)
TTL openTime + toIntervalMonth(3)
SETTINGS index_granularity = 8192;
