import asyncio
import logging
import csv
import os
from datetime import datetime
from config import TARGET_URLS
from pipeline import PriceMonitorPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("price_monitor.log"),
        logging.StreamHandler()
    ]
)

def check_price_changes(new_results, filename="prices.csv"):
    if not os.path.exists(filename):
        logging.info("CSV файл не найден - это первый запуск")
        return

    old_prices = {}
    try:
        with open(filename, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                old_prices[row["URL"]] = float(row["Price"])
    except Exception as error:
        logging.error(f"Ошибка при чтении CSV: {error}")
        return

    for res in new_results:
        if not res:
            continue

        url = res["url"]
        title = res["data"]["title"]
        new_price = res["data"]["price"]

        if url not in old_prices:
            logging.info(f"Новый товар добавлен: {url}")
            print(f"✨ Новый товар добавлен: [{title}] - {new_price}")
            continue

        old_price = old_prices[url]
        if new_price < old_price:
            diff = old_price - new_price
            logging.info(f"Цена упала на {diff} для {url}")
            print(f"📉 Цена упала! [{title}]: было {old_price}, стало {new_price} (экономия: {diff})")
        elif new_price > old_price:
            diff = new_price - old_price
            logging.info(f"Цена выросла на {diff} для {url}")
            print(f"📈 Цена выросла. [{title}]: было {old_price}, стало {new_price} (+{diff})")
        else:
            print(f"➡️ Цена не изменилась. [{title}]: {new_price}")


def save_to_csv(results, filename="prices.csv"):
    if not results:
        logging.warning("Нет результатов для сохранения в CSV")
        return

    try:
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["URL", "Title", "Price", "In Stock", "Timestamp"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                if not res:
                    continue
                writer.writerow({
                    "URL": res["url"],
                    "Title": res["data"]["title"],
                    "Price": res["data"]["price"],
                    "In Stock": res["data"]["in_stock"],
                    "Timestamp": datetime.now().isoformat()
                })
        logging.info(f"Результаты сохранены в {filename}")
    except Exception as error:
        logging.error(f"Ошибка при сохранении CSV: {error}")


async def main():
    monitor = PriceMonitorPipeline()
    try:
        await monitor.init()
        results = await monitor.run(TARGET_URLS)
        check_price_changes(results)
        save_to_csv(results)
    finally:
        await monitor.close()


if __name__ == "__main__":
    asyncio.run(main())
