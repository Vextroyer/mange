"""API"""
import base64
from datetime import datetime
from functools import wraps, lru_cache
import inspect
import logging
import pathlib
import pickle
import time

from sqlalchemy import create_engine
from sqlalchemy.sql import text, select
from sqlalchemy.orm import sessionmaker, scoped_session

from mange.conf import settings
from mange.db import (
    Base,
    Company,
    Bill,
    Item,
    load_backup,
)
from mange.log import logged

log = logging.getLogger("global")

DB = settings.DATABASES["default"]
URL = DB["engine"]


def benchmark(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        start = time.time()

        result = method(*args, **kwargs)

        end = round(time.time() - start, 3)
        log.info("benchmarked method %s %s", method.__name__, end)
        return result

    return wrapper


def loggedmethod(method):
    """
    Log a CRUD method and confirm its successful execution
    version: 1.0.1
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        method_data = inspect.getfullargspec(method)
        mname = method.__name__.lstrip("_")  # ignore encapsulation
        method_type = mname.split("_")[0].upper()
        # + 1 because of self
        try:
            self.logger.info(
                "_%s_ %s %s",
                method_type,
                [
                    f"{method_data.args[index + 1]}={value}"
                    for index, value in enumerate(args)
                ],
                kwargs,
            )
        except IndexError as exc:
            raise IndexError(
                f"Too many arguments for {mname}. Maybe you used positional arguments intead of key-value arguments?"
            )

        res = method(self, *args, **kwargs)

        self.logger.debug("_%s_ --success--", method_type)
        return res

    return wrapper


@logged
class Client:
    def __init__(self, url=URL, config=None):
        config = config or {}
        self.url = url
        self.config = config
        self.logger.info("Started %s. Engine: %s", self.__class__.__name__, URL)

        db_file = pathlib.Path(url.split("///")[-1])
        assert db_file.exists(), f"DB file doesn't exist! {db_file}"
        assert db_file.stat().st_size > 0, "DB file is just an empty file!"

        self.engine = create_engine(url)

        self.engine = create_engine(url)

        self.session = scoped_session(sessionmaker(bind=self.engine, **config))  # pylint: --disable=C0103

    def __delete__(self, obj):
        self.session.rollback()
        self.session.close()

    def __str__(self):
        return f"[Client] ({self.url=} {self.config=})"

    # low level
    @loggedmethod
    def _get(self, Obj, /, **kwargs):
        """Low level GET implementation"""
        query = self.session.query(Obj)
        for k, v in kwargs.items():
            query = query.filter(getattr(Obj, k) == v)

        return query

    @loggedmethod
    def _create(self, Obj, /, **kwargs):
        """Low level insert implementation"""
        obj = Obj(**kwargs)
        self.session.add(obj)
        # self.session.commit()

        return obj

    @loggedmethod
    def update(self, obj, /, **kwargs):
        """Update implementation. Feel free to use this directly"""

        if isinstance(obj, Base):
            for k, v in kwargs.items():
                setattr(obj, k, v)
            # self.session.add(obj)
            # self.session.commit()
        elif getattr(obj, "__name__"):
            # model class
            query = self.session.query(obj)
            obj = query.update(**kwargs).one()
        else:
            raise AssertionError(f"{obj} is not update-able")

        return obj

    def _get_or_create(self, Obj, /, **kwargs):
        """Low level select or insert  implementation"""
        obj = self._get(Obj, **kwargs).all()
        if not obj:
            return self._create(Obj, **kwargs)
        obj = obj[0]
        return obj

    # crud
    def create_company(self, /, **kwargs):
        return self._create(Company, **kwargs)

    def get_company(self, /, **kwargs):
        return self._get(Company, **kwargs)

    def create_bill(self, /, **kwargs):
        return self._create(Bill, **kwargs)

    def get_bill(self, /, **kwargs):
        return self._get(Bill, **kwargs)

    def create_item(self, /, **kwargs):
        return self._create(Item, **kwargs)

    def get_item(self, /, **kwargs):
        return self._get(Item, **kwargs)

    def liquidate_bill(self, company):
        """
        Given a company, liquidate its bill.
        """
        over_limit = company.over_limit
        cost = company.calculate()

        company.last_reading = company.reading
        self.update(company, last_reading=company.reading)

        self.create_bill(
            company=company,
            date=datetime.today(),
            reading=company.reading,
            over_limit=over_limit
        )
    
    # high-level
    def total_comsumption(self, company, start_date, end_date):
        # select * between start_date and end_date
        return NotImplemented

    def list_alerts(self, company):
        # select * where over_limit=1 and company_id = company.id
        return NotImplemented

    def average_comsumption(self, company, start_date, end_date):
        """
        Monthly comsumption.
        """
        # return total/calc_months()
        return NotImplemented

    def over_comsumption(self, start_date, end_date):
        # select company, over_limit where over_limit > 0
        return NotImplemented

    def predict_comsumption(self, start_date, end_date):
        # interpolate???
        return NotImplemented

    def compare_comsumption(self, start_date, end_date, changes_date):
        """
        a frecuencia de uso (>every time one uses an item they must register it manually wtf)
        """
        return "won't fix"
    
    def list_alerts(self, company):
        #return over_comsumption.where(Company.id = company.id)
        return NotImplemented
