from typing import Any, Dict, List, Optional, Union

import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import re
from copy import deepcopy

from pathlib import Path
from tqdm import tqdm

## Custom lib
from config import PathConfig, ScraperConfig
import utils

class DataFetcher:
    def __init__(self) -> None:
        ## Init session
        self.session = requests.session()

        assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()
        self.session.hooks["response"] = [assert_status_hook]

        retry_strategy = Retry(**ScraperConfig.retry_strategy)
        adapter = HTTPAdapter(max_retries=retry_strategy)

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        ## POST data
        self.request_url = ScraperConfig.request_url
        self.request_headers = ScraperConfig.request_headers
        self.POST_data = ScraperConfig.data_without_trdDd

    def get_response(self, trdDd: Union[str, int], mktId: str="ALL"):
        if not isinstance(mktId, str) or mktId.upper() not in ["ALL", "STK", "KSQ", "KNX"]:
            raise Exception("Wrong mktId. Select from ['ALL', 'STK', 'KSQ', 'KNX']")
        
        trdDd = utils.validate_date2str(trdDd)

        POST_data = deepcopy(self.POST_data)
        POST_data["trdDd"] = trdDd
        POST_data["mktId"] = mktId
        res = self.session.post(self.request_url, data=POST_data, headers=self.request_headers)

        return res, trdDd
        
    def parse_response(res, trdDd: str):
        data = res.json()["OutBlock_1"]
        df = pd.DataFrame(data)
        df.loc[:, "trdDd"] = int(trdDd)

        return df
        

class CacheGenerator:
    def __init__(self, start_date, end_date) -> None:
        self.start_date = utils.validate_date2str(start_date)
        self.end_date = utils.validate_date2str(end_date)
        self.data_fetcher = DataFetcher()

    def fetch_lv1(self, mktId="ALL", is_save=False): # start_date & end_date are inclusive
        date_range = pd.date_range(self.start_date, self.end_date)
        date_range = [date.strftime("%Y%m%d") for date in date_range]

        # TODO: Fetch data by year and save it to free memory
        lv1_df = pd.DataFrame()
        for trdDd in tqdm(date_range):
            res, trdDd = self.data_fetcher.get_response(trdDd, mktId)
            df = self.data_fetcher.parse_response(res, trdDd)
            lv1_df.append(df, ignore_index=True)
        
        if is_save:
            lv1_df.to_pickle(f"{self.start_date}_to_{self.end_date}.pkl")

        return lv1_df