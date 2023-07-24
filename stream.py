import asyncio
import datetime
import os
import logging

from clickhouse_driver import Client as ClickHouseClient
from binance import AsyncClient, BinanceSocketManager
from binance.client import Client as BinanceClient

binance_api_key = os.environ.get("api_key")
binance_api_secret = os.environ.get("api_secret")

clickhouse_password = os.environ.get("clickhouse_password")
if clickhouse_password:
    clickhouse_client = ClickHouseClient(
        host="localhost", port=9000, password=clickhouse_password
    )
else:
    clickhouse_client = ClickHouseClient(host="localhost", port=9000)


async def stream_and_update(symbols):
    async_client = await AsyncClient.create(
        api_key=binance_api_key, api_secret=binance_api_secret
    )
    socket_manager = BinanceSocketManager(async_client)

    # Create a separate WebSocket connection for each symbol
    async def process_symbol(symbol):
        kline_socket = socket_manager.kline_socket(symbol=symbol)

        async with kline_socket as stream:
            while True:
                msg = await stream.recv()
                print("MSG:")
                print(msg)

                # Process the received message
                # Extract the necessary fields (symbol, timestamp, open, high, low, close, volume, close_time)
                symbol = msg["s"]
                open_time = datetime.datetime.fromtimestamp(msg["k"]["t"] / 1e3)
                close_time = datetime.datetime.fromtimestamp(msg["k"]["T"] / 1e3)
                open_price = float(msg["k"]["o"])
                high_price = float(msg["k"]["h"])
                low_price = float(msg["k"]["l"])
                close_price = float(msg["k"]["c"])
                volume = float(msg["k"]["v"])

                # Insert the data into the ClickHouse table
                query = (
                    f"INSERT INTO klines (symbol, openTime, closeTime, openPrice, highPrice, lowPrice, closePrice, volume) "
                    f"VALUES ('{symbol}', '{open_time}', '{close_time}', {open_price}, {high_price}, {low_price}, {close_price}, {volume})"
                )
                clickhouse_client.execute(query)

                logging.info(
                    f"Received data for symbol {symbol}: {open_time} - {close_time}"
                )

    tasks = [process_symbol(symbol) for symbol in symbols]
    await asyncio.gather(*tasks)


def get_symbols(base=None, quote=None):
    if base and quote:
        raise Exception("Only one of base and quote can be used")
    binance_client = BinanceClient(binance_api_key, binance_api_secret)
    exchange_info = binance_client.get_exchange_info()
    if base:
        symbols = [
            symbol["symbol"]
            for symbol in exchange_info["symbols"]
            if symbol["baseAsset"] == base
        ]
    elif quote:
        symbols = [
            symbol["symbol"]
            for symbol in exchange_info["symbols"]
            if symbol["quoteAsset"] == quote
        ]
    else:
        symbols = [symbol["symbol"] for symbol in exchange_info["symbols"]]
    return symbols


if __name__ == "__main__":
    symbols = get_symbols(quote="USDT")
    asyncio.run(stream_and_update(symbols))
