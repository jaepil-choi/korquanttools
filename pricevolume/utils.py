from typing import Any, Dict, List, Optional, Union

def validate_date2str(yyyymmdd: Union[str, int]) -> str:
    try:
        if not (19900101 < int(yyyymmdd) < 21001231):
            raise Exception("Wrong yyyymmdd range")
        
        yyyymmdd = str(yyyymmdd)
    except ValueError as e:
        raise Exception("Wrong type (ValueError)")
    except Exception as e:
        raise e
    
    return yyyymmdd

    