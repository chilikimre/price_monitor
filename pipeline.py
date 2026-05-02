import asyncio
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
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async def close(self):
        pass

    async def fetch_url(self, url: str, shop_type: str) -> str:
        headers = {"User-Agent": get_random_user_agent()}
        proxy = await get_proxy()
        
        loop = asyncio.get_event_loop()
        
        try:
            html_content = await loop.run_in_executor(
                None, 
                fetch_with_curl, 
                url, 
                headers, 
                REQUEST_TIMEOUT
            )
            return html_content
            
        except Exception as e:
            raise Exception(f"Fetch failed: {str(e)}")

    async def process_item(self, item: Dict[str, Any], attempt: int = 0) -> Dict[str, Any]:
        url = item["url"]
        shop_type = item["shop_type"]
            
        async with self.semaphore:
            try:
                html_content = await self.fetch_url(url, shop_type)
                data = parse_content(html_content, shop_type)
                return {"url": url, "data": data}
            except Exception as e:
                if attempt < 3:
                    delay = calculate_backoff(attempt)
                    await asyncio.sleep(delay)
                    return await self.process_item(item, attempt + 1)
                else:
                    logger.error(f"Failed to process {url} after retries: {str(e)}")
                    return {"url": url, "data": {"title": "Ошибка", "price": 0.0, "in_stock": False}}

    async def run(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        tasks = [self.process_item(item) for item in items]
        results = await asyncio.gather(*tasks)
        return results