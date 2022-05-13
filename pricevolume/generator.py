from typing import Any, Dict, List, Optional, Union

import pandas as pd
import numpy as np

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import re
import itertools
from copy import deepcopy

from pathlib import Path
from tqdm import tqdm

## Custom lib
from pricevolume.config import PathConfig, ScraperConfig
from pricevolume.processor import Preprocessor, Lv2Converter
from pricevolume.utils import DateUtil

class DataFetcher:
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
        self.request_url = self.scraper_config.request_url
        self.request_headers = self.scraper_config.request_headers
        self.POST_data = self.scraper_config.data_without_trdDd

    def get_response(self, trdDd: Union[str, int], mktId: str="ALL"):
        if not isinstance(mktId, str) or mktId.upper() not in ["ALL", "STK", "KSQ", "KNX"]:
            raise Exception("Wrong mktId. Select from ['ALL', 'STK', 'KSQ', 'KNX']")
        
        trdDd = DateUtil.validate_date2str(trdDd)

        POST_data = deepcopy(self.POST_data)
        POST_data["trdDd"] = trdDd
        POST_data["mktId"] = mktId
        res = self.session.post(self.request_url, data=POST_data, headers=self.request_headers)

        return res, trdDd
        
    def parse_response(self, res, trdDd: str):
        data = res.json()["OutBlock_1"]
        df = pd.DataFrame(data)
        df.loc[:, "trdDd"] = int(trdDd)

        return df
        

class CacheGenerator:
    def __init__(self, start_date, end_date, mktId="ALL") -> None:
        self.DM_name = "KRX_pricevolume"

        self.path_config = PathConfig()

        self.start_date = DateUtil.validate_date2str(start_date)
        self.end_date = DateUtil.validate_date2str(end_date)
        self.mktId = mktId

        self.data_fetcher = DataFetcher()

        self.lv1_df = None
        self.lv2_df = None

    def fetch_lv1(self, is_save=False): # start_date & end_date are inclusive
        date_range = pd.date_range(self.start_date, self.end_date)
        date_range = [date.strftime("%Y%m%d") for date in date_range]

        # TODO: Fetch data by year and save it to free memory
        self.lv1_df = pd.DataFrame()
        for trdDd in tqdm(date_range):
            res, trdDd = self.data_fetcher.get_response(trdDd, self.mktId)
            df = self.data_fetcher.parse_response(res, trdDd)
            self.lv1_df = self.lv1_df.append(df, ignore_index=True)

        return self.lv1_df
    
    def process_lv1(self, is_save=True):
        self.lv1_df = Preprocessor.comma_number_2_float(
            self.lv1_df,
            columns=self.lv1_df.columns[4:15],
        )
        self.lv1_df = Preprocessor.nullstr_2_nan(
            self.lv1_df,
            columns=self.lv1_df.columns[4:15],
            nullstr="-"
        )
    
    def convert_2_lv2(self, value_column, date_column="trdDd", sid_column="ISU_SRT_CD", is_save=True):
        self.lv2_df = Lv2Converter.convert_2_lv2(
            self.lv1_df,
            date_column=date_column,
            sid_column=sid_column,
            value_column=value_column,
            method="pd_pivot",
            )


# TODO: Move meta DM classes into separate file. 
class CacheSaver:
    frequencies = ['minute', 'hour', 'day', 'week', 'month', 'quarter', 'year']
    frequency2dtype = { # no quarter
        'minute': 'datetime64[m]',
        'hour': 'datetime64[h]',
        'day': 'datetime64[D]',
        'week': 'datetime64[W]',
        'month': 'datetime64[M]',
        'year': 'datetime64[W]',
    }

    def __init__(self, DM_name, frequency='day',) -> None:
        self.DM_name = DM_name

        frequency = frequency.lower()
        if frequency not in self.frequencies:
            raise Exception(f"{frequency} not in frequencies list: {self.frequencies}")
        self.frequency = frequency # currently not being used. 
        
        self.df = None
        self.min_date = None
        self.max_date = None

        self.path_config = PathConfig()
        self.base_dir = (self.path_config.cache_path / self.DM_name)


    def load_df(self, df, datetime_format, date_col_name=None):
        self.df = df # NOT deepcopying the given df. Changes will affect the original df. 
        
        if isinstance(self.df.index, pd.DatetimeIndex):
            self.min_date = min(self.df.index)
            self.max_date = max(self.df.index)
            
            return 

        try:
            if date_col_name:
                self.df.loc[:, date_col_name] = pd.to_datetime(self.df[date_col_name], format=datetime_format)
                self.min_date = min(df.loc[:, date_col_name])
                self.max_date = max(df.loc[:, date_col_name])
            else: # index is date
                self.index = pd.to_datetime(self.df.index, format=datetime_format)
                self.min_date = min(df.index)
                self.max_date = max(df.index)

            return

        except:
            if date_col_name:
                raise Exception(f"Cannot convert data to datetime format from column: {date_col_name}")
            else:
                raise Exception(f"Cannot convert data to datetime format from index column")
        
    def generate_dirs(self, data_list:list, is_lv1=True, frequency="month"):

        # freq_dtype = CacheSaver.frequency2dtype[frequency] # TODO: Dynamically change directory structure based on frequency parameter
        years = DateUtil.inclusive_daterange(self.min_date, self.max_date, "year")
        years = [DateUtil.npdate2str(y)['year'] for y in years]
        months = DateUtil.inclusive_daterange(self.min_date, self.max_date, "month")
        months = [DateUtil.npdate2str(m)['month'] for m in months]

        if is_lv1:
            data_list = ["lv1"] + data_list

        for data_name in data_list:
            p = self.base_dir / data_name
            
            for year, month in itertools.product(years, months):
                (p / year / month).mkdir(parents=True, exist_ok=True)
            
        return
    
    def save_cache(self, data_name):
        group_by_month = self.df.groupby(pd.Grouper(key=None, freq="M")) # key=None means index
        group_by_month = [g for _, g in group_by_month]

        years = DateUtil.inclusive_daterange(self.min_date, self.max_date, "year")
        years = [DateUtil.npdate2str(y)['year'] for y in years]
        months = DateUtil.inclusive_daterange(self.min_date, self.max_date, "month")
        months = [DateUtil.npdate2str(m)['month'] for m in months]

        p = self.base_dir / data_name
        for (year, month), df in zip(itertools.product(years, months), group_by_month):
            min_date = min(df.index).date()
            max_date = max(df.index).date()
            
            save_path = p / year / month
            filename = f"{min_date}_{max_date}.pkl"

            df.to_pickle(save_path / filename)

                
        
        

        
        