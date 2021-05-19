import io
import json
import zipfile
from datetime import datetime

import pandas as pd
import requests

from mysite.redis_client import RedisClient


def get_bhavcopy_url(bhavcopy_name: str):
    """
    Example Url

    https://www.bseindia.com/download/BhavCopy/Equity/EQ190521_CSV.ZIP
    """

    bhavcopy_homepage = 'https://www.bseindia.com/download/BhavCopy/Equity'
    return f'{bhavcopy_homepage}/{bhavcopy_name}.ZIP'


def extract_data(csv_file: str):
    df = pd.read_csv(csv_file)
    return df.T.loc[['SC_CODE', 'SC_NAME', 'OPEN', 'HIGH', 'LOW', 'CLOSE']].to_dict()


class Bhavcopy:
    BHAVCOPY_NAME = 'EQ%d%m%y_CSV'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

    def __init__(self, logger):
        self.logger = logger
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
        }
        self.r = RedisClient().connect()

    # @param {datetime} date
    #
    # @return [request, bhavcopy_name]
    def get_bhavcopy(self, date: datetime):
        bhavcopy_name = f'{date.strftime(self.BHAVCOPY_NAME)}'
        bhavcopy_url = get_bhavcopy_url(bhavcopy_name)
        self.logger.info(f'Fetch data from {bhavcopy_url}')

        return requests.get(url=bhavcopy_url, headers=self.headers), bhavcopy_name

    # @param {datetime} today
    #
    # @return [request, bhavcopy_name]
    def fetch_data(self, today: datetime):
        response, bhavcopy_name = self.get_bhavcopy(today)

        if response.status_code == 200:
            self.logger.info(f'Response received of {bhavcopy_name} with Stats Code: {response.status_code}')
            return response, bhavcopy_name

        self.logger.warn(f'Response received of {bhavcopy_name} with Stats Code: {response.status_code}')

    # @param {datetime} date
    #
    # @return Boolean
    def valid_date(self, date):
        if not self.r.get('date'):
            return True
        return datetime.strptime(self.r.get('date').decode(), self.DATE_FORMAT) < date

    def populate_data_into_redis(self, csv_file, date):
        if not self.valid_date(date):
            self.logger.warn('Skip!!! Populating data into redis')
            return

        data = extract_data(csv_file)
        self.logger.info('populating data into redis')
        self.r.flushall()
        self.r.set('date', date.strftime(self.DATE_FORMAT))

        # Insert data into Redis
        for d in data.values():
            key = f"BSE:{d.get('SC_CODE')}:{d.get('SC_NAME').strip().upper()}"
            self.r.set(key, json.dumps(d))

    def perform(self):
        today = datetime.today()
        response, file_name = self.fetch_data(today=today)

        if not response:
            self.logger.error('Unable to fetch bhavcopy')
            return

        # Extract CSV file from zip
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        csv_file = zip_file.extract(file_name.replace('_', '.'))
        self.populate_data_into_redis(csv_file, today)
