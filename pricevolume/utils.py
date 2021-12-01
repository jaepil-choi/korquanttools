from typing import Any, Dict, List, Optional, Union
import pandas as pd

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

def validate_date2str(yyyymmdd: Union[str, int]) -> str:
    if validate_date(yyyymmdd):
        return str(yyyymmdd)
    else:
        raise Exception("Date validation failed")

def validate_date2int(yyyymmdd: Union[str, int]) -> int:
    if validate_date(yyyymmdd):
        return int(yyyymmdd)
    else:
        raise Exception("Date validation failed")