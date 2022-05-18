from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

import datetime

class DateUtil:
    @staticmethod
    def validate_date(yyyymmdd: Union[str, int], start="19900101", end="21000101") -> bool:
        """Check wheter the given input has valid date format & value regardless of type

        Args:
            yyyymmdd (Union[str, int]): date format in yyyymmdd, i.e: %Y%m%d
            start (str, optional): Start date of sanity check. Defaults to "19900101".
            end (str, optional): End date of sanity check. Defaults to "21000101".

        Returns:
            bool: True if the input has a valid date format & value. 
        """        

        start_date = pd.to_datetime(start)
        end_date = pd.to_datetime(end)

        if isinstance(yyyymmdd, (str, int)):
            date = str(yyyymmdd)

            try:
                date = pd.to_datetime(yyyymmdd)
                return (start_date < date < end_date)
            except:
                return False
        
        if isinstance(yyyymmdd, datetime.datetime) or isinstance(yyyymmdd, np.datetime64):
            try:
                date = pd.to_datetime(yyyymmdd)
                return (start_date < date < end_date)
            except:
                return False
        else:
            return False

    @staticmethod
    def validate_date2str(yyyymmdd: Union[str, int]) -> str:
        if DateUtil.validate_date(yyyymmdd):
            return str(yyyymmdd)
        else:
            raise Exception(f"Date validation failed. Given: yyyymmdd = {yyyymmdd}")

    @staticmethod
    def validate_date2int(yyyymmdd: Union[str, int]) -> int:
        if DateUtil.validate_date(yyyymmdd):
            return int(yyyymmdd)
        else:
            raise Exception(f"Date validation failed. Given: yyyymmdd = {yyyymmdd}")
    
    @staticmethod
    def intDate_2_timestamp(yyyymmdd: int):
        date = str(yyyymmdd)
        return pd.to_datetime(date, format="%Y%m%d")
    
    @staticmethod
    def timestamp_2_intDate(timestamp, format="%Y%m%d"):
        date = timestamp.strftime(format=format)
        return int(date)
    
    @staticmethod
    def inclusive_daterange(start_date, end_date, frequency):
        # TODO: Maybe just use pd.date_range in the future, but the problem is that it's not inclusive.
        frequencies = ["day", "month", "year"]
        frequency2dtype = {
        'day': 'datetime64[D]',
        'month': 'datetime64[M]',
        'year': 'datetime64[Y]',
        }
        assert frequency in frequencies

        date_range = np.arange(start_date, end_date + pd.Timedelta(days=1), dtype="datetime64[D]")
        date_range = np.unique(date_range.astype(frequency2dtype[frequency]))

        return date_range

    @staticmethod
    def npdate2str(npdate):
        npdate = npdate.astype("datetime64[D]")
        year, month, date = npdate.astype(str).split('-')
        
        return {'year': year, 'month': month, 'date': date}