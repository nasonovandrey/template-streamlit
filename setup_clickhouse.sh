#!/bin/bash

# Start the ClickHouse server (assuming it's already installed and configured)
clickhouse-server &

# Wait for ClickHouse to start (you can adjust the sleep duration as needed)
sleep 10

clickhouse-client < klines.sql
