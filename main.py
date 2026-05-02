import asyncio
import logging
import csv
from datetime import datetime
from pipeline import PriceMonitorPipeline
from config import TARGET_URLS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('price_monitor.log'),
        logging.StreamHandler()
    ]
)

def check_price_changes(new_results, filename='prices.csv'):
    """Сравнивает цены с предыдущей записью"""
    import os
    
    if not os.path.exists(filename):
        logging.info("CSV файл не найден - это первый запуск")
        return
    
    # Читаем старые цены
    old_prices = {}
    try:
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                url = row['URL']
                price = float(row['Price'])
                old_prices[url] = price
    except Exception as e:
        logging.error(f"Ошибка при чтении CSV: {str(e)}")
        return
    
    # Сравниваем с новыми результатами
    for res in new_results:
        if res:
            url = res['url']
            new_price = res['data']['price']
            title = res['data']['title']
            
            if url in old_prices:
                old_price = old_prices[url]
                if new_price < old_price:
                    diff = old_price - new_price
                    print(f"📉 Цена упала! [{title}]: было {old_price}, стало {new_price} (экономия: {diff})")
                    logging.info(f"Цена упала на {diff} для {url}")
                elif new_price > old_price:
                    diff = new_price - old_price
                    print(f"📈 Цена выросла. [{title}]: было {old_price}, стало {new_price} (+{diff})")
                else:
                    print(f"➡️ Цена не изменилась. [{title}]: {new_price}")
            else:
                print(f"✨ Новый товар добавлен: [{title}] - {new_price}")
                logging.info(f"Новый товар: {url}")

def save_to_csv(results, filename='prices.csv'):
    """Сохраняет результаты в CSV-файл"""
    if not results:
        logging.warning("Нет результатов для сохранения в CSV")
        return
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['URL', 'Title', 'Price', 'In Stock', 'Timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for res in results:
                if res:
                    writer.writerow({
                        'URL': res['url'],
                        'Title': res['data']['title'],
                        'Price': res['data']['price'],
                        'In Stock': res['data']['in_stock'],
                        'Timestamp': datetime.now().isoformat()
                    })
        
        logging.info(f"Результаты сохранены в {filename}")
    except Exception as e:
        logging.error(f"Ошибка при сохранении CSV: {str(e)}")

async def main():
    monitor = PriceMonitorPipeline()
    try:
        await monitor.init()
        results = await monitor.run(TARGET_URLS)
        
        check_price_changes(results)
        save_to_csv(results)
    finally:
        await monitor.close()

if __name__ == '__main__':
    asyncio.run(main())