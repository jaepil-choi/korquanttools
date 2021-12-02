import pandas as pd
import numpy as np

from pathlib import Path

from abc import ABC, abstractmethod

## Custom lib
from pricevolume.config import PathConfig
import pricevolume.utils

class BaseDM(ABC): # TODO: Make BaseDM include all other metadata / separate BaseDM to other framework module
    @property
    @abstractmethod
    def _name(self):
        raise NotImplementedError
    
    @property
    @abstractmethod
    def _description(self):
        raise NotImplementedError
    
    @property
    @abstractmethod
    def _birthday(self):
        raise NotImplementedError
    
    @property
    @abstractmethod
    def _min_date(self):
        raise NotImplementedError
    
    # TODO: Add @mindate.setter for validation
    
    @abstractmethod
    def load_data(self):
        raise NotImplementedError

class DM(BaseDM):
    _name = "KRX_pricevolume"
    _description = "Basic raw price-volume data imported from KRX website. Has KOSPI, KOSDAQ, KONEX stocks."
    _birthday = 20211203
    _min_date = 19990101
    _load_path = PathConfig.cache_path

    def __init__(self, start, end=21001231, is_tradingdays=True, sid_list=None) -> None:
        super().__init__()

        self.start = start
        self.end = end
        self.sid_list = sid_list if sid_list else None

        if is_tradingdays:
            self.date_list = 

        if DM._min_date > start:
            raise ValueError(f"Start date({start}) earlier than min date({DM._min_date})")

    def load_data(self, start, end, temp_file_name, load_path=None): # TODO: Remove temp file name and replace with data_name (KOSPI, KOSDAQ, KONEX)
        if not load_path:
            load_path = DM._load_path
        
        df = pd.read_pickle(load_path / temp_file_name) ## 
        
        # TODO: 현재는 lv1 을 불러와서 여기서 바꾸는데 절대 그러면 안된다. lv2 cache를 생성해서 그걸 불러올 수 있어야 함. 
        
    def get_data(self, data_name):
        pass