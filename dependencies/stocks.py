import yfinance as yf
import pandas as pd


class StocksProvider:
    def __init__(self):
        pass

    @staticmethod
    def validate_tickers(tickers: list[str]):
        invalid_tickers = []
        for ticker in tickers:
            t = yf.ticker.Ticker(ticker)
            if not t.stats():
                invalid_tickers.append(ticker)
        if invalid_tickers:
            raise KeyError(f'Unknown tickers: {invalid_tickers}')

    @staticmethod
    def get_current_price(tickers: list[str]) -> pd.DataFrame:
        StocksProvider.validate_tickers(tickers)
        info = yf.download(' '.join(tickers), period='5d', progress=False, prepost=True, interval='1h', threads=True)
        prices = info['Close'].fillna(method='ffill').iloc[-1, :]
        return prices

    @staticmethod
    def get_historical_price(tickers: list[str], period: str, interval: str = '1d') -> pd.DataFrame:
        StocksProvider.validate_tickers(tickers)
        info = yf.download(' '.join(tickers), period=period, progress=False, prepost=True, interval=interval, threads=True)
        prices = info['Close'].fillna(method='ffill')
        return prices
