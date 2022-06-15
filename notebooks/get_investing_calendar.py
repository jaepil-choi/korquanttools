import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup as bs

import pandas as pd
import numpy as np

import re
import unicodedata


## custom libs

from korquanttools.pricevolume.config import PathConfig, ScraperConfig
from . import config

class EarningsCalandarDataFetcher:
    def __init__(self) -> None:
        ## Init config
        self.scraper_config = ScraperConfig()
        
        ## Init session
        self.session = requests.session()

        assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()
        self.session.hooks["response"] = [assert_status_hook]

        retry_strategy = Retry(**self.scraper_config.retry_strategy)
        adapter = HTTPAdapter(max_retries=retry_strategy)

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        ## POST data
        self.request_url = config.REQUEST_URL
        self.request_headers = config.REQUEST_HEADERS
        self.POST_data = {
            "country[]": "11", # south korea
            "dateFrom": None,
            "dateTo": None,
            "currentTab": "custom",
            "limit_from": "0",
            "submitFilters": "1",
            # "last_time_scope": "1437523200",
            # "byHandler": "true",
            }
        
        ## Parsing data
        weekdays = [
            'Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday',
            'Sunday',
        ]

        self.weekdays_re = re.compile('(' + '|'.join(weekdays) + ')')
        self.space_re = re.compile('^\s*$')

    def get_response(self, from_date, to_date):
        self.POST_data['dateFrom'] = from_date # "2022-01-01"
        self.POST_data['dateTo'] = to_date # "2022-05-30"

        res = self.session.post(self.request_url, data=self.POST_data, headers=self.request_headers)

        return res

    def parse_earnings_text(self, root_bs_text):
        split = root_bs_text.split('\n')
        split = [s for s in split if not re.match(self.space_re, s)]
        split = [unicodedata.normalize('NFKD', s) for s in split ]

        split_idx = []
        for idx, item in enumerate(split):
            if re.search(self.weekdays_re, item):
                split_idx.append(idx)
        
        data_list = []
        for start_idx, end_idx in zip(split_idx, split_idx[1:] + [None]):
            data_text_list = split[start_idx:end_idx]

            data = {
                'date': data_text_list[0], # Tuesday, January 4, 2022
                'company': data_text_list[1], # K Auction (102370)
                'EPS' : data_text_list[2], # 606.73
                'EPS_forecast': data_text_list[3], # /  --
                'revenue': data_text_list[4], # 14.39B
                'revenue_forecast': data_text_list[5], # /  --
            }

            data_list.append(data)

        return data_list

    def parse_response(self, res):
        root_bs = bs(res.json()['data'], 'html.parser')
        root_text = root_bs.get_text()

        data_list = self.parse_earnings_text(root_text)

        return data_list

    def get_data(self, start_year, end_year, additional_from_to_list=[]):
        years = list(range(start_year, end_year))
        yearly_from_to_list = [(f'{y}-01-01', f'{y}-12-31') for y in years]
        yearly_from_to_list += additional_from_to_list

        all_data_list = []
        for from_date, to_date in yearly_from_to_list:
            res = self.get_response(from_date, to_date)
            data_list = self.parse_response(res)
            all_data_list += data_list
        
        return all_data_list
    
    def preprocess_data(self, data_list):
        earnings_calendar_df = pd.DataFrame(data_list)

        earnings_calendar_df.loc[:, 'date'] = earnings_calendar_df.loc[:, 'date'].apply(self.parse_date)
        earnings_calendar_df.loc[:, 'codename'] = earnings_calendar_df.loc[:, 'company'].apply(lambda x: self.parse_company(x)[0])
        earnings_calendar_df.loc[:, 'sid'] = earnings_calendar_df.loc[:, 'company'].apply(lambda x: self.parse_company(x)[1])
        earnings_calendar_df.loc[:, 'EPS'] = earnings_calendar_df.loc[:, 'EPS'].apply(self.parse_value)
        earnings_calendar_df.loc[:, 'EPS_forecast'] = earnings_calendar_df.loc[:, 'EPS_forecast'].apply(self.parse_value)
        earnings_calendar_df.loc[:, 'revenue'] = earnings_calendar_df.loc[:, 'revenue'].apply(self.parse_value)
        earnings_calendar_df.loc[:, 'revenue_forecast'] = earnings_calendar_df.loc[:, 'revenue_forecast'].apply(self.parse_value)
    
        earnings_calendar_df.drop('company', axis=1, inplace=True)

        return earnings_calendar_df
    
    @staticmethod
    def parse_date(investings_date):
        investings_date = investings_date.strip()
        format = "%A, %B %d, %Y"
        
        return pd.to_datetime(investings_date, format=format)
    
    @staticmethod
    def parse_company(company_str):
        pattern_re = re.compile('(.+)\((\d{6})\)')
        codename = re.search(pattern_re, company_str)[1]
        sid = re.search(pattern_re, company_str)[2]

        return codename, sid
    
    @staticmethod
    def parse_value(value):
        B = 1
        
        if 'B' in value:
            value = value.replace('B', '')
            B = 1e+9
        
        value = value.replace('/', '')
        value = value.replace(',', '')
        value = value.strip()
        
        try:
            value = float(value)
            
            return value * B
        
        except:
            return None

# fetcher = EarningsCalandarDataFetcher()
# data_list = fetcher.get_data(2014, 2022, additional_from_to_list=[('2022-01-01', '2022-05-30')])
# earnings_calendar_df = pd.DataFrame(data_list)