import requests
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

class AlphaVantageService:
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key=None):
        self.api_key = api_key or settings.ALPHA_VANTAGE_API_KEY
        if not self.api_key:
            logger.error("No Alpha Vantage API key provided")
            raise ValueError("Alpha Vantage API key is required")
    
    def get_quote(self, symbol):
        """Get the latest price for a stock symbol"""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "Global Quote" in data and data["Global Quote"]:
                quote = data["Global Quote"]
                return {
                    "symbol": quote.get("01. symbol"),
                    "price": Decimal(quote.get("05. price", 0)),
                    "change": Decimal(quote.get("09. change", 0)),
                    "change_percent": quote.get("10. change percent", "0%").strip('%'),
                    "volume": int(quote.get("06. volume", 0)),
                    "latest_trading_day": quote.get("07. latest trading day"),
                }
            else:
                if "Note" in data:
                    logger.warning(f"API limit reached: {data['Note']}")
                    raise Exception("API rate limit reached. Please try again later.")
                logger.error(f"Failed to get quote for {symbol}: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error for {symbol}: {str(e)}")
            return None
    
    def get_daily_time_series(self, symbol, outputsize="compact"):
        """Get daily time series for a symbol
        
        Args:
            symbol: The stock symbol
            outputsize: 'compact' (last 100 data points) or 'full' (up to 20 years)
        """
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": outputsize,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "Time Series (Daily)" in data:
                time_series = data["Time Series (Daily)"]
                result = []
                
                for date, values in time_series.items():
                    result.append({
                        "date": date,
                        "open": Decimal(values["1. open"]),
                        "high": Decimal(values["2. high"]),
                        "low": Decimal(values["3. low"]),
                        "close": Decimal(values["4. close"]),
                        "volume": int(values["5. volume"])
                    })
                
                # Sort by date, newest first
                result.sort(key=lambda x: x["date"], reverse=True)
                return result
            else:
                if "Note" in data:
                    logger.warning(f"API limit reached: {data['Note']}")
                    raise Exception("API rate limit reached. Please try again later.")
                logger.error(f"Failed to get time series for {symbol}: {data}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error for {symbol}: {str(e)}")
            return []
    
    def search_symbol(self, keywords):
        """Search for a symbol based on keywords"""
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": keywords,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "bestMatches" in data:
                matches = data["bestMatches"]
                result = []
                
                for match in matches:
                    result.append({
                        "symbol": match.get("1. symbol"),
                        "name": match.get("2. name"),
                        "type": match.get("3. type"),
                        "region": match.get("4. region"),
                        "currency": match.get("8. currency"),
                    })
                
                return result
            else:
                if "Note" in data:
                    logger.warning(f"API limit reached: {data['Note']}")
                    raise Exception("API rate limit reached. Please try again later.")
                logger.error(f"Failed to search for symbol {keywords}: {data}")
                return []
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error for search {keywords}: {str(e)}")
            return []
            
    def update_asset_price(self, asset):
        """Update the current price of an asset"""
        try:
            quote = self.get_quote(asset.symbol)
            if quote and "price" in quote:
                asset.current_price = quote["price"]
                asset.last_updated = timezone.now()
                asset.save()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating price for {asset.symbol}: {str(e)}")
            return False
    
    def update_assets_prices(self, assets):
        """Update prices for multiple assets"""
        updated_count = 0
        for asset in assets:
            # Only update if last update was more than 15 minutes ago or if never updated
            if not asset.last_updated or timezone.now() - asset.last_updated > timedelta(minutes=15):
                if self.update_asset_price(asset):
                    updated_count += 1
        return updated_count
