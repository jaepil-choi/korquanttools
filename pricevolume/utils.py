from typing import Any, Dict, List, Optional, Union
import pandas as pd

class DateUtil:
    @staticmethod
    def validate_date(yyyymmdd: Union[str, int], start="19900101", end="21000101") -> bool:
        if not isinstance(yyyymmdd, [str, int]):
            return False
        
        start_date = pd.to_datetime(start)
        end_date = pd.to_datetime(end)

        try:
            date = pd.to_datetime(yyyymmdd)
            return (start_date < date < end_date)
        except:
            return False

    @staticmethod
    def validate_date2str(yyyymmdd: Union[str, int]) -> str:
        if DateUtil.validate_date(yyyymmdd):
            return str(yyyymmdd)
        else:
            raise Exception("Date validation failed")

    @staticmethod
    def validate_date2int(yyyymmdd: Union[str, int]) -> int:
        if DateUtil.validate_date(yyyymmdd):
            return int(yyyymmdd)
        else:
            raise Exception("Date validation failed")
    
    @staticmethod
    def intDate_2_timestamp(yyyymmdd: int):
        date = str(yyyymmdd)
        return pd.to_datetime(date, format="%Y%m%d")
    
    @staticmethod
    def timestamp_2_intDate(timestamp, format="%Y%m%d"):
        date = timestamp.strftime(format=format)
        return int(date)