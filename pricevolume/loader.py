import pandas as pd
import numpy as np

from pathlib import Path
import re

from abc import ABC, abstractmethod

## Custom lib
from pricevolume.config import PathConfig
from pricevolume.utils import DateUtil

class BaseDM(ABC): # TODO: Make BaseDM include all other metadata / separate BaseDM to other framework module
    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError
    
    @property
    @abstractmethod
    def description(self):
        raise NotImplementedError
    
    @property
    @abstractmethod
    def birthday(self):
        raise NotImplementedError
    
    @property
    @abstractmethod
    def min_date(self): # TODO: Add some sort of validation
        raise NotImplementedError
    
    @property
    @abstractmethod
    def load_path(self):
        raise NotImplementedError
    
    @property
    @abstractmethod
    def data_list(self):
        raise NotImplementedError
    def check_cache_exist(self, date): # TODO: Make better after building tradingday DM
        year = str(date.year)
        month = f'{date.month:02}'
        
        p = self.load_path / year / month
        f = list(p.glob('*.pkl')) # -> list

        if f == []:
            is_exist = False
        elif len(f) == 1:
            is_exist = f[0].is_file()
        elif len(f) >= 2:
            raise Exception(f"More than one cache file exists at {p}")
        else:
            raise Exception(f"Unknown Error. Check f = {f}")
        
        
        day1_re = re.compile('\d{4}-\d{2}-01_\d{4}-\d{2}-\d{2}')
        is_startfromday1 = True if re.match(day1_re, f.stem) else False

        if is_exist and is_startfromday1:
            return True
        else:
            return False
        

    def get_info(self):
        info = f'''
        * DM name: {self.name}
        * DM description: {self.description}
        * birthday: {self.birthday}
        * DM period: {self.min_date} ~ 
        * Available data: {self.data_list}
        '''
        print(info)

        return
        

class DM(BaseDM):
    name = "KRX_pricevolume"
    description = "Basic price-volume data imported from KRX website & NAVER finance. Has KOSPI, KOSDAQ, KONEX stocks."
    birthday = 20211203
    min_date = 19990101
    data_list = ["open", "high", "low", "close", "adj_close", "return", "volume", "market_cap"]

    load_path = PathConfig.cache_path / name

    def __init__(self, start, end=21001231, is_tradingday=True, sid_list=None) -> None:
        # super().__init__()

        self.start = start
        self.end = end
        self.sid_list = sid_list if sid_list else None

        if is_tradingday:
            is_tradingday = False # Temporarily set to False
            # self.date_list = ... # TODO: Download data first and then filter. 

        if DM.min_date > start:
            raise ValueError(f"Start date({start}) earlier than min date({DM._min_date})")
        
        
        # TODO: 현재는 lv1 을 불러와서 여기서 바꾸는데 절대 그러면 안된다. lv2 cache를 생성해서 그걸 불러올 수 있어야 함. 
        
    def get_data(self, data_name):
        pass