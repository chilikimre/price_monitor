import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = 0

MAX_CONCURRENT_REQUESTS = 1 # Для Ozon ставим 1
REQUEST_TIMEOUT = 15
CACHE_TTL_SECONDS = 3600

TARGET_URLS = [
    {"url": "https://www.citilink.ru/product/smartfon-oppo-a6x-256gb-6gb-t-fioletovyi-3g-4g-2sim-6-75-ips-720x1570-2160554/", "shop_type": "citilink"},
]