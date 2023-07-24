#!/bin/bash

./setup_clickhouse.sh
python3 ./stream.py &
streamlit run app.py

