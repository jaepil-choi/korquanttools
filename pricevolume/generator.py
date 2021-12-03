from typing import Any, Dict, List, Optional, Union

import pandas as pd
import numpy as np

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import re
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
        
        if is_save:
            self.path_config.cache_path.mkdir(parents=True, exist_ok=True)
            self.lv1_df.to_pickle(self.path_config.cache_path / f"{self.mktId}_{self.start_date}_to_{self.end_date}_lv1_df.pkl", )

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

        if is_save:
            self.path_config.cache_path.mkdir(parents=True, exist_ok=True)
            self.lv1_df.to_pickle(self.path_config.cache_path / f"{self.mktId}_{self.start_date}_to_{self.end_date}_lv1_df.pkl", )
    
    def convert_2_lv2(self, value_column, date_column="trdDd", sid_column="ISU_SRT_CD", is_save=True):
        self.lv2_df = Lv2Converter.convert_2_lv2(
            self.lv1_df,
            date_column=date_column,
            sid_column=sid_column,
            value_column=value_column,
            method="pd_pivot",
            )

        if is_save:
            self.path_config.cache_path.mkdir(parents=True, exist_ok=True)
            self.lv2_df.to_pickle(self.path_config.cache_path / f"{self.mktId}_{self.start_date}_to_{self.end_date}_lv2_df.pkl", )

