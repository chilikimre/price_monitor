import random
from typing import Optional
from curl_cffi import requests as cffi_requests

def get_random_user_agent() -> str:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    return random.choice(USER_AGENTS)

async def get_proxy() -> Optional[str]:
    return None

def calculate_backoff(attempt: int) -> float:
    base_delay = 2 ** attempt
    jitter = random.uniform(0, 1)
    return min(base_delay + jitter, 60)

def fetch_with_curl(url: str, headers: dict, timeout: int) -> str:
    full_headers = headers.copy()
    chrome_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Referer': 'https://www.citilink.ru/',
    }
    full_headers.update(chrome_headers)
    response = cffi_requests.get(url, headers=full_headers, timeout=timeout, impersonate='chrome110')
    if response.status_code == 200:
        return response.text
    raise Exception(f"HTTP {response.status_code}")