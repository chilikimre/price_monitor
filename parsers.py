import json
import logging
from typing import Dict, Any
from lxml import html

logger = logging.getLogger(__name__)

class ParseError(Exception):
    pass

def clean_price(price_str: str) -> float:
    cleaned = price_str.replace(' ', '').replace(',', '.')
    return float(cleaned)

def parse_citilink(content: str) -> Dict[str, Any]:
    logger.debug("parse_citilink content preview: %s", content[:500])
    tree = html.fromstring(content)

    title = "Не найдено"
    title_candidates = tree.xpath('//h1/text()') or tree.xpath('//title/text()')
    if title_candidates:
        title = title_candidates[0].strip() or title

    price = 0.0
    price_meta = tree.xpath('//meta[@property="product:price:amount"]/@content')
    if price_meta:
        try:
            price = clean_price(price_meta[0])
        except Exception as error:
            logger.debug("parse_citilink failed to parse meta price: %s", error)

    if price == 0.0:
        scripts = tree.xpath('//script[@type="application/ld+json"]/text()')
        for script_text in scripts:
            try:
                data = json.loads(script_text)
                candidates = [data] if isinstance(data, dict) else data
                for item in candidates:
                    offers = item.get('offers') if isinstance(item, dict) else None
                    if isinstance(offers, dict):
                        price_value = offers.get('price')
                        if price_value:
                            price = clean_price(str(price_value))
                            break
                    elif isinstance(offers, list):
                        for offer in offers:
                            price_value = offer.get('price')
                            if price_value:
                                price = clean_price(str(price_value))
                                break
                        if price > 0.0:
                            break
                if price > 0.0:
                    break
            except Exception as error:
                logger.debug("parse_citilink failed to parse JSON-LD: %s", error)

    in_stock = bool(tree.xpath('//button[contains(text(), "В корзину")]'))

    if title == "Не найдено" or price == 0.0:
        logger.error(
            "parse_citilink did not extract required data, title=%s, price=%s",
            title,
            price,
        )
        logger.debug("parse_citilink html preview: %s", content[:500])

    return {
        "title": title,
        "price": price,
        "in_stock": in_stock,
    }

PARSERS_MAP = {
    "citilink": parse_citilink
}

def parse_content(content: str, shop_type: str) -> Dict[str, Any]:
    parser = PARSERS_MAP.get(shop_type)
    if not parser:
        raise ParseError(f"Неизвестный тип магазина: {shop_type}")
    return parser(content)