from os import stat
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import numpy as np

## Custom lib
from config import PathConfig
import utils

class Preprocessor:
    @staticmethod
    def comma_number_2_float(df: pd.DataFrame, columns: list, digit_sep=",", is_copy=True):
        if is_copy:
            df = df.copy()
        
        df.loc[:, columns] = df.loc[:, columns].replace(regex=digit_sep, value="")
        
        return df
    
    @staticmethod
    def nullstr_2_nan(df: pd.DataFrame, columns: list, nullstr: str, is_copy=True):
        if is_copy:
            df = df.copy()
        
        df.loc[:, columns] = df.loc[:, columns].replace(nullstr, value=np.nan)

        return df
