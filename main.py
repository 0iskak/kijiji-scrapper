import logging
import sys
from multiprocessing.pool import ThreadPool
from typing import Optional

import requests
from bs4 import BeautifulSoup

from Item import Item
from db import db, table_name

logger = logging.getLogger('')
logger.setLevel(logging.INFO)
sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
logger.addHandler(sh)

items: list[Item] = []
pageNo = 0
while True:
    try:
        pageNo += 1
        logger.info(f'Parsing page: {pageNo}')
        url = f'https://www.kijiji.ca/b-apartments-condos/city-of-toronto/page-{pageNo}/c37l1700273'
        r = requests.get(url, allow_redirects=False)
        if r.is_redirect:
            if pageNo == 1:
                r = requests.get(url)
            else:
                break
        page = BeautifulSoup(r.content, "lxml")
        main = page.select_one('main')

        for item in main.select('.search-item'):
            items.append(Item.parse(item))
    except Exception as e:
        continue

logger.info(f'Parsed {len(items)} items')


def save(item: Item) -> Optional[str]:
    try:
        logger.info(f'Saving {item.item_id}')
        query = Item.replace(**item.dict)
        try:
            query.execute()
        except:
            pass

        return str(query) + ';\n'
    except:
        return None


Item.create_table()
with open('items.sql', 'w+', encoding='UTF-8') as file:
    file.write(
        db.execute_sql(f'SHOW CREATE TABLE `{table_name}`;').fetchone()[1]
        + ';\n'
    )

    with ThreadPool() as pool:
        str_items = tuple(filter(lambda s: s is not None, pool.map(save, items)))
        logger.info(f'Saved {len(str_items)} items')
        file.writelines(str_items)
