from typing import Dict, Any
from lxml import html

class ParseError(Exception):
    pass

def clean_price(price_str: str) -> float:
    """Вспомогательная функция для обработки строк цен"""
    # Удаляем пробелы, заменяем запятую на точку
    cleaned = price_str.replace(' ', '').replace(',', '.')
    return float(cleaned)

def parse_citilink(content: str) -> Dict[str, Any]:
    tree = html.fromstring(content)
    
    # Название товара в <h1> с классом содержащим 'title'
    title_elem = tree.xpath('//h1[contains(@class, "title")]')
    title = title_elem[0].text_content().strip() if title_elem else "Не найдено"
    
    # Цена в мета-теге product:price:amount
    price_meta = tree.xpath('//meta[@property="product:price:amount"]/@content')
    price = float(price_meta[0]) if price_meta else 0.0
    
    # Наличие по наличию кнопки 'В корзину'
    in_stock = bool(tree.xpath('//button[contains(text(), "В корзину")]'))
    
    return {
        "title": title,
        "price": price,
        "in_stock": in_stock
    }

PARSERS_MAP = {
    'citilink': parse_citilink
}

def parse_content(content: str, shop_type: str) -> Dict[str, Any]:
    parser = PARSERS_MAP.get(shop_type)
    if not parser:
        raise ParseError(f"Неизвестный тип магазина: {shop_type}")
    return parser(content)