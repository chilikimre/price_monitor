from typing import Dict, Any

class ParseError(Exception):
    pass

def parse_ozon(content: str) -> Dict[str, Any]:
    """Парсинг Ozon через JSON в HTML"""
    from lxml import html
    import json
    
    tree = html.fromstring(content)
    scripts = tree.xpath('//script[@type="application/json"]/text()')
    
    title = "Не найдено"
    price = 0.0
    in_stock = False
    found_data = False
    
    for script_text in scripts:
        try:
            data = json.loads(script_text)
            
            def find_product_info(obj, depth=0):
                nonlocal title, price, in_stock, found_data
                if depth > 5 or found_data: 
                    return
                
                if isinstance(obj, dict):
                    if 'title' in obj and ('price' in obj or 'currentPrice' in obj):
                        title = obj['title']
                        p_val = obj.get('price', obj.get('currentPrice'))
                        if isinstance(p_val, dict):
                            price = float(p_val.get('value', 0))
                        else:
                            try: 
                                price = float(p_val)
                            except: 
                                price = 0.0
                        in_stock = obj.get('isAvailable', True)
                        found_data = True
                        return
                    
                    for key, value in obj.items():
                        if found_data: 
                            return
                        find_product_info(value, depth + 1)
                        
                elif isinstance(obj, list):
                    for item in obj:
                        if found_data: 
                            return
                        find_product_info(item, depth + 1)

            find_product_info(data)
            if found_data: 
                break
                
        except: 
            continue
            
    if not found_data:
        raise ParseError("Не удалось найти данные о товаре на Ozon")

    return {
        "title": title,
        "price": price,
        "in_stock": in_stock
    }

def parse_wildberries(content: str) -> Dict[str, Any]:
    """Парсинг Wildberries через JSON в HTML"""
    from lxml import html
    import json
    
    tree = html.fromstring(content)
    scripts = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')
    
    title = "Не найдено"
    price = 0.0
    in_stock = False
    found_data = False
    
    for script_text in scripts:
        try:
            data = json.loads(script_text)
            
            def find_product_info(obj, depth=0):
                nonlocal title, price, in_stock, found_data
                if depth > 10 or found_data: 
                    return
                
                if isinstance(obj, dict):
                    if 'name' in obj and ('salePriceU' in obj or 'priceU' in obj):
                        title = obj['name']
                        p_val = obj.get('salePriceU', obj.get('priceU', 0))
                        price = float(p_val) / 100  # цена в копейках
                        # Проверяем наличие через stocks или qty
                        stocks = obj.get('stocks', [])
                        qty = obj.get('qty', 0)
                        in_stock = len(stocks) > 0 or qty > 0
                        found_data = True
                        return
                    
                    for key, value in obj.items():
                        if found_data: 
                            return
                        find_product_info(value, depth + 1)
                        
                elif isinstance(obj, list):
                    for item in obj:
                        if found_data: 
                            return
                        find_product_info(item, depth + 1)

            find_product_info(data)
            if found_data: 
                break
                
        except: 
            continue
            
    if not found_data:
        raise ParseError("Не удалось найти данные о товаре на Wildberries")

    return {
        "title": title,
        "price": price,
        "in_stock": in_stock
    }

def parse_dns(content: str) -> Dict[str, Any]:
    """Парсинг DNS через HTML"""
    from lxml import html
    import json
    
    tree = html.fromstring(content)
    
    # Название товара
    title_elements = tree.xpath("//h1[contains(@class, 'name')]/text()")
    if not title_elements:
        title_elements = tree.xpath("//h1/text()")
    title = title_elements[0].strip() if title_elements else "Не найдено"
    
    # Цена
    price = 0.0
    price_meta = tree.xpath("//meta[@property='product:price:amount']/@content")
    if price_meta:
        try:
            price = float(price_meta[0])
        except:
            price = 0.0
    else:
        # Ищем в JSON-LD
        scripts = tree.xpath('//script[@type="application/ld+json"]/text()')
        for script_text in scripts:
            try:
                data = json.loads(script_text)
                if isinstance(data, dict) and data.get('@type') == 'Product':
                    offers = data.get('offers', {})
                    if isinstance(offers, dict):
                        price_val = offers.get('price')
                        if price_val:
                            price = float(price_val)
                            break
            except:
                continue
    
    # Наличие
    in_stock = False
    buy_buttons = tree.xpath("//button[contains(text(), 'Купить')]")
    if buy_buttons:
        in_stock = True
    else:
        in_stock_elements = tree.xpath("//*[contains(@class, 'in-stock') or contains(@class, 'available')]")
        in_stock = len(in_stock_elements) > 0
    
    if title == "Не найдено" and price == 0.0:
        raise ParseError("Не удалось найти данные о товаре на DNS")
    
    return {
        "title": title,
        "price": price,
        "in_stock": in_stock
    }

def parse_citilink(content: str) -> Dict[str, Any]:
    """Парсинг Citilink через HTML"""
    from lxml import html
    import json
    
    tree = html.fromstring(content)
    
    # Название товара
    title_elements = tree.xpath("//h1[contains(@class, 'title')]/text()")
    if not title_elements:
        title_elements = tree.xpath("//h1/text()")
    title = title_elements[0].strip() if title_elements else "Не найдено"
    
    # Цена
    price = 0.0
    price_meta = tree.xpath("//meta[@property='product:price:amount']/@content")
    if price_meta:
        try:
            price = float(price_meta[0])
        except:
            price = 0.0
    else:
        # Ищем в JSON-LD
        scripts = tree.xpath('//script[@type="application/ld+json"]/text()')
        for script_text in scripts:
            try:
                data = json.loads(script_text)
                if isinstance(data, dict) and data.get('@type') == 'Product':
                    offers = data.get('offers', {})
                    if isinstance(offers, dict):
                        price_val = offers.get('price')
                        if price_val:
                            price = float(price_val)
                            break
            except:
                continue
    
    # Наличие
    in_stock = False
    cart_buttons = tree.xpath("//button[contains(text(), 'В корзину')]")
    if cart_buttons:
        in_stock = True
    else:
        available_elements = tree.xpath("//*[contains(text(), 'В наличии') or contains(@class, 'available')]")
        in_stock = len(available_elements) > 0
    
    if title == "Не найдено" and price == 0.0:
        raise ParseError("Не удалось найти данные о товаре на Citilink")
    
    return {
        "title": title,
        "price": price,
        "in_stock": in_stock
    }

PARSERS_MAP = {
    'ozon': parse_ozon,
    'wildberries': parse_wildberries,
    'dns': parse_dns,
    'citilink': parse_citilink
}

def parse_content(content: str, shop_type: str) -> Dict[str, Any]:
    parser = PARSERS_MAP.get(shop_type)
    if not parser:
        raise ParseError(f"Неизвестный тип магазина: {shop_type}")
    return parser(content)