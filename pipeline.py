import asyncio
import json
import time
import logging
from typing import Dict, Any, List
from utils import get_random_user_agent, get_proxy, calculate_backoff, fetch_with_curl
from parsers import parse_content, ParseError
from config import MAX_CONCURRENT_REQUESTS, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

class PriceMonitorPipeline:
    def __init__(self):
        self.semaphore = None

    async def init(self):
        """Инициализация ресурсов"""
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async def close(self):
        """Закрытие ресурсов"""
        pass

    async def fetch_url(self, url: str, shop_type: str) -> str:
        headers = {"User-Agent": get_random_user_agent()}
        proxy = await get_proxy() 
        
        loop = asyncio.get_event_loop()
        
        try:
            # Запускаем синхронную функцию в пуле потоков, чтобы не блокировать event loop
            html_content = await loop.run_in_executor(
                None, 
                fetch_with_curl, 
                url, 
                headers, 
                REQUEST_TIMEOUT,
                None  # cookies
            )
            return html_content
            
        except Exception as e:
            raise Exception(f"Fetch failed: {str(e)}")

    async def process_item(self, item: Dict[str, Any], attempt: int = 0):
        url = item["url"]
        shop_type = item["shop_type"]
            
        async with self.semaphore:
            try:
                logger.info(f"[FETCHING] {url} (Attempt {attempt + 1})")
                html_content = await self.fetch_url(url, shop_type)
                
                # Парсинг
                data = parse_content(html_content, shop_type)
                
                result = {
                    "url": url,
                    "shop_type": shop_type,
                    "data": data,
                    "timestamp": time.time()
                }
                
                logger.info(f"[SUCCESS] Parsed {url}: {data['price']}")
                return result

            except Exception as e:
                logger.warning(f"[ERROR] Failed to process {url}: {str(e)}")
                
                if attempt < 3:
                    delay = calculate_backoff(attempt)
                    logger.info(f"[RETRY] Scheduling retry for {url} in {delay:.2f}s")
                    await asyncio.sleep(delay)
                    return await self.process_item(item, attempt + 1)
                else:
                    logger.error(f"[FAIL] Max retries reached for {url}")
                    return None

    async def run(self, urls: List[Dict[str, Any]]):
        await self.init()
        try:
            tasks = [self.process_item(item) for item in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful = [r for r in results if r is not None and not isinstance(r, Exception)]
            logger.info(f"Processing complete. Success: {len(successful)}/{len(urls)}")
            return successful
        finally:
            await self.close()