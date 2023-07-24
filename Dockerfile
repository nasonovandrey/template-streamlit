FROM yandex/clickhouse-server

WORKDIR /app
COPY . /app

RUN rm /etc/apt/sources.list.d/*
RUN apt-get update
RUN apt-get install -y python3 python3-pip 

RUN pip3 install streamlit python-binance matplotlib pandas numpy clickhouse-driver

EXPOSE 80 9000

CMD ["./entrypoint.sh"]
