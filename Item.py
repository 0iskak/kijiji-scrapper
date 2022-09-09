import re
from datetime import datetime, timedelta

from bs4 import Tag
from peewee import *

from db import db, table_name


class Item(Model):
    class Meta:
        database = db
        db_table = table_name

    item_id = PrimaryKeyField(null=True)
    image = CharField(null=True)
    title = CharField(null=True)
    date = CharField(null=True)
    city = CharField(null=True)
    beds = CharField(null=True)
    description = CharField(null=True)
    price = DecimalField(null=True, decimal_places=2)
    currency = CharField(null=True)

    def __init__(self, item_id: int, image: str, title: str, date: str, city: str, beds: str, description: str,
                 price: float,
                 currency: str) -> None:
        self.dict = {}
        for key, value in locals().items():
            if key in ('__class__', 'self'):
                continue
            if isinstance(value, str):
                value = value.replace("'", "''")

            self.dict[key] = value
        super().__init__(**self.dict)

    @classmethod
    def parse(cls, item: Tag) -> 'Item':
        item_id = int(item.get('data-listing-id'))
        image = item.select_one('img') \
            .get('data-src')

        info = item.select_one('.info')
        title = info.select_one('a[class*=title]') \
            .get_text(strip=True)
        date = info.select_one('.date-posted') \
            .get_text(strip=True)
        try:
            date = datetime.strptime(date, '%d/%m/%Y')
        except:
            is_yesterday = date == 'Yesterday'
            date = datetime.now()
            if is_yesterday:
                date -= timedelta(days=1)
        date = date.strftime('%d-%m-%Y')

        city = item.select_one('.location') \
            .findChild() \
            .get_text(strip=True)
        description = item.select_one('.description') \
            .get_text(strip=True)
        price_text = item.select_one('.price').get_text(strip=True)
        try:
            price = re.findall('[\\d,.]+', price_text)[0]
        except IndexError:
            price = None
        currency = None if price is None \
            else price_text.replace(price, '')
        if price is not None:
            price = float(price.replace(',', ''))

        rental_info = item.select_one('.rental-info')
        beds = re.sub(
            '^Beds:\n +', '',
            rental_info.select_one('.bedrooms').get_text(strip=True)
        )

        return cls(
            item_id,
            image,
            title,
            date,
            city,
            beds,
            description,
            price,
            currency
        )
