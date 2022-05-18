# from sqlite3 import Date 
import pandas as pd
import numpy as np

from pathlib import Path
import re

from abc import ABC, abstractmethod

## Custom lib
from pricevolume.config import PathConfig
from pricevolume.utils import DateUtil

from pricevolume.generator import CacheGenerator, CacheSaver

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

    @abstractmethod
    def generate_data(self):
        raise NotImplementedError

    def get_data(self, data_name, level=2):
        assert data_name in DM.data_list
        assert level in [1, 2]

        start = DateUtil.intDate_2_timestamp(self.start)
        end = DateUtil.intDate_2_timestamp(self.end)
        today = pd.Timestamp.today()

        if end >= today:
            end = today

        inclusive_date_range = DateUtil.inclusive_daterange(start, end, "month")
        inclusive_date_range = inclusive_date_range.astype("datetime64[D]")
        # TODO: 없는 데이터 generate 하며 on-demand로 get_data 해오기 
        # 월별로 데이터 cache 있는지 확인해서 붙이다가, 
        # 없으면 - last 월이 아닌 이상 그 월 start, end 해서 cache generation 
        # 해야하는 기간 목록 쭉 모으고 while 그 목록이 비어있지 않는 한, cache generation 해서 없는 부분 채움. 
        
        df = pd.DataFrame()

        for date in inclusive_date_range: # yyyy-mm-01
            year = DateUtil.npdate2str(date)['year']
            month = DateUtil.npdate2str(date)['month']
            p = self.load_path / data_name / year / month

            if self.check_cache_exist(data_name, date):
                f = list(p.glob('*.pkl'))[0]
                monthly_df = pd.read_pickle(p / f)
                df = df.append(monthly_df, ignore_index=False)
            else:
                self.generate_data(start, end)

                f = list(p.glob('*.pkl'))[0]
                monthly_df = pd.read_pickle(p / f)
                df = df.append(monthly_df, ignore_index=False)
        
        return df
        
    def check_cache_exist(self, data_name, date): # TODO: Make better after building tradingday DM
        date = pd.to_datetime(date)
        
        year = str(date.year)
        month = f'{date.month:02}'
        
        p = self.load_path / data_name / year / month
        f = list(p.glob('*.pkl')) # -> list

        if f == []:
            is_exist = False
        elif len(f) == 1:
            is_exist = f[0].is_file()
        elif len(f) >= 2:
            raise Exception(f"More than one cache file exists at {p}")
        else:
            raise Exception(f"Unknown Error. Check f = {f}")
        
        if is_exist:
            day1_re = re.compile('\d{4}-\d{2}-01_\d{4}-\d{2}-\d{2}')
            is_startfromday1 = True if re.match(day1_re, f[0].stem) else False
        else:
            is_startfromday1 = False

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
    data_list = ["open", "high", "low", "close", "adj_close", "return", "volume", "dollarvolume", "marketcap"]

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
    
    def generate_data(self, start_date, end_date):
        cg = CacheGenerator(start_date, end_date, mktId="ALL")
        cs = CacheSaver(self.name, frequency="day")

        data_col_mapping = {
            "open": "TDD_OPNPRC",
            "high": "TDD_HGPRC",
            "low": "TDD_LWPRC",
            "close": "TDD_CLSPRC",
            "volume": "ACC_TRDVOL",
            "dollarvolume": "ACC_TRDVAL",
            "marketcap": "MKTCAP",
        }

        cg.fetch_lv1()
        cg.process_lv1()
        cs.load_df(cg.lv1_df, "%Y%m%d", date_col_name="trdDd")
        cs.generate_dirs(self.data_list, is_lv1=True, frequency="month")
        cs.save_cache("lv1", lv1_key="trdDd")

        for data_name, col_name in data_col_mapping.items():
            cg.convert_2_lv2(col_name)
            cs.load_df(cg.lv2_df, "%Y%m%d", date_col_name=None)
            cs.save_cache(data_name)

# class ModuleSelector: 
#     pass
    # def load_DM(self, start, end, DM_name, load_path=None):
    #     if load_path is not None:
    #         load_path = self.load_path