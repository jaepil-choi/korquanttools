from os import stat
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import numpy as np

## Custom lib
from financedashboard.pricevolume.config import PathConfig

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
    
    @staticmethod
    def columns_2_float(df: pd.DataFrame, columns: list, is_copy=True):
        if is_copy:
            df = df.copy()
        
        df.loc[:, columns] = df.loc[:, columns].astype(float)

        return df

class Lv2Converter:
    @staticmethod
    def convert_2_lv2(
        lv1_df: pd.DataFrame, 
        date_column: str, 
        sid_column: str, 
        value_column: str, 
        method="pd_pivot",
        ):
        if method not in ["pd_pivot", "np_iter", "np_broadcast"]:
            raise ValueError
        
        if method == "pd_pivot":
            lv2_df = lv1_df.pivot(
                index=date_column, 
                columns=sid_column, 
                values=value_column
                )
            
            return lv2_df
        
        elif method == "np_iter": # TODO: Separate each method so that numba can be used
            date_list = lv1_df.loc[:, date_column].unique()
            sid_list = lv1_df.loc[:, sid_column].unique()

            lv2_arr = np.empty((len(date_list), len(sid_list)))
            lv2_arr[:] = np.nan

            date_list_mapper = dict(zip(date_list, range(len(date_list))))
            sid_list_mapper = dict(zip(sid_list, range(len(sid_list))))

            temp_df = lv1_df.loc[:, [date_column, sid_column, value_column]].copy()
            temp_arr = np.array(temp_df)

            for row in temp_arr:
                date_idx = date_list_mapper[row[0]]
                sid_idx = sid_list_mapper[row[1]]
                value = row[2]

                lv2_arr[date_idx, sid_idx] = value
            
            lv2_df = pd.DataFrame(lv2_arr, index=date_list, columns=sid_list)
            
            return lv2_df
        
        elif method == "np_broadcast":
            date_list = lv1_df.loc[:, date_column].unique()
            sid_list = lv1_df.loc[:, sid_column].unique()

            lv2_arr = np.empty((len(date_list), len(sid_list)))
            lv2_arr[:] = np.nan

            date_list_mapper = dict(zip(date_list, range(len(date_list))))
            sid_list_mapper = dict(zip(sid_list, range(len(sid_list)))) 

            date_list_arr = np.array(list(map(lambda x: date_list_mapper[x], lv1_df[date_column]))) # row
            date_list_arr = date_list_arr[:, None]

            sid_list_arr = np.array(list(map(lambda x: sid_list_mapper[x], lv1_df[sid_column]))) # column
            sid_list_arr = sid_list_arr[None, :]            

            value_list_arr = np.array(lv1_df.loc[:, value_column])

            lv2_arr[date_list_arr, sid_list_arr] = value_list_arr

            lv2_df = pd.DataFrame(lv2_arr, index=date_list, columns=sid_list)

            return lv2_df

            


    