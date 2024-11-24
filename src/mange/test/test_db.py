from datetime import datetime
import os
from pathlib import Path
import unittest

from mange.db import *
from mange.api import *
from mange.conf import settings

db = settings.DATABASES["default"]
ENGINE = db["engine"]

TEST_DIR = settings.TEST_DIR

def build_test_db(
        name=ENGINE,
    ):
    """
    Create test database and schema.
    """
    engine = create_engine(name)

    # Nuke everything and build it from scratch.
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    return engine

class Test_API(unittest.TestCase):
    
    def setUp(self):
        build_test_db()
        self.client = Client()

    def tearDown(self):
        pass

    def test_login(self):
        user = self.client.create_user(name="blob", password="doko")
        self.client.session.commit()

        self.assertEqual(self.client.login(name="blob", password="doko"), user.token)

    def test_liquidate_bill(self):
        company = self.client.create_company(name="blobcorp", last_reading=0, reading=0, limit=100)
        self.client.session.commit()

        company.reading = 50

        bill = self.client.liquidate_bill(company)

        self.assertEqual(company.last_reading, company.reading)
        self.assertEqual(bill.over_limit, 0)

        company.reading = 150

        bill = self.client.liquidate_bill(company)
        self.assertEqual(bill.over_limit, 50)

    def test_total_consumption(self):
        company = self.client.create_company(name="blobcorp", last_reading=0, reading=100, limit=9999)
        self.client.session.commit()

        company.reading = 150
        bill = self.client.liquidate_bill(company, date=datetime(2000, 10, 1))

        company.reading = 300
        bill = self.client.liquidate_bill(company, date=datetime(2000, 10, 2))

        company.reading = 500
        bill = self.client.liquidate_bill(company, date=datetime(2000, 10, 3))

        self.assertEqual(
            self.client.total_consumption(
                company,
                start_date=datetime(2000, 10, 1),
                end_date=datetime(2000, 10, 3)
            ),
            350,
        )

    def test_over_consumption(self):
        company = self.client.create_company(name="blobcorp", last_reading=0, reading=1, limit=0)
        self.client.session.commit()
        bill = self.client.liquidate_bill(company, date=datetime(2000, 10, 1))

        self.assertEqual(
            self.client.over_consumption(start_date=datetime(2000, 10, 1), end_date=datetime(2000, 10, 1)),
            [bill],
        )



def main_suite() -> unittest.TestSuite:
    s = unittest.TestSuite()
    load_from = unittest.defaultTestLoader.loadTestsFromTestCase
    s.addTests(load_from(Test_API))
    
    return s

def run():
    t = unittest.TextTestRunner()
    t.run(main_suite())
