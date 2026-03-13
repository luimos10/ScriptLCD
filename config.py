import os

API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")

dias = 30
workers = 6
max_retries = 6
retry_base_delay = 1.0
request_timeout = 10
show_progress = True
