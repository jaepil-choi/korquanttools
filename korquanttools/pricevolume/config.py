from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Union

from pathlib import Path
import sys

BASE_PATH = Path(__file__).parent.resolve() # pricevolume/

@dataclass
class PathConfig:
    cache_path: Union[str, Path] = field(
        default=BASE_PATH / "cache",
        metadata={"help": "Cache path for historical KRX price & volume data"}
    )

@dataclass
class ScraperConfig:
    request_url: str = field(
        default="http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd",
        metadata={"help": "KRX all stocks price & volume (http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020101)"}
    )
    request_headers: Dict[str, str] = field(
        default_factory=lambda: {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9,ko-KR;q=0.8,ko;q=0.7,ja;q=0.6",
            "Connection": "keep-alive",
            "Content-Length": "98",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            # "Cookie": "__smVisitorID=MOg5nSVvce5; JSESSIONID=Zm2tghqTUaVeWZwBoqGf5XDEl5p1ay0OKwMa1bMRQnDGQJ8xpyLTaXTZyGHWcjVY.bWRjX2RvbWFpbi9tZGNvd2FwMi1tZGNhcHAxMQ==",
            "Host": "data.krx.co.kr",
            "Origin": "http://data.krx.co.kr",
            "Referer": "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020101",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            },
        metadata={"help": "Request header data used in the browser"}
        )
    data_without_trdDd: Dict[str, Optional[str]] = field(
        default_factory=lambda: {
            "bld": "dbms/MDC/STAT/standard/MDCSTAT01501",
            "mktId": "ALL", # KOSPI: "STK", KOSDAQ: "KSQ", KONEX: "KNX"
            "trdDd": None, # format like: "20211029"
            "share": "1",
            "money": "1",
            "csvxls_isNo": "false",
            },
        metadata={"help": "POST data without trading date field(trdDd)"}
        )
    retry_strategy: Dict[int, Union[int, list]] = field(
        default_factory=lambda: {
            "total": 10,
            "status_forcelist": [413, 429, 500, 502, 503, 504],
            "method_whitelist": ["GET", "POST"],
            "backoff_factor": 2,
            },
        metadata={"help": "Retry strategy arguments"}
    )

    # TODO: 괜히 dataclass 쓰면 쓸데없이 일이 복잡해진다. lambda : deepcopy({...}) 해줘야 함. 