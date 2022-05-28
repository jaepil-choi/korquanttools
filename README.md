```
   __                                __  __            __  
  / /_____  _______ ___ _____ ____  / /_/ /____  ___  / /__
 /  '_/ _ \/ __/ _ `/ // / _ `/ _ \/ __/ __/ _ \/ _ \/ (_-<
/_/\_\\___/_/  \_, /\_,_/\_,_/_//_/\__/\__/\___/\___/_/___/
                /_/                                        
                                                                                                      
```                                                                                                                                                       
                                                                                                                                                          
# Project description                                                                                                                                                          

`korquanttools` is an on-going project to make quantitative analysis on Korean stock market easier. 

# Features

- Scrape KOSPI, KOSDAQ stock universe price-volume data by given period directly from KRX
- Load KOSPI, KOSDAQ stock universe without survivorship bias (delisted stocks are included)
- Cache the downloaded data for faster access later on.
- More coming soon

# Installation

Not yet deployed to pypi. 

Either clone the repository or download the repository to use the package. 

# Quickstart

```python

# Import data library
from korquanttools.pricevolume.loader import KRXPriceDM

# Set start date and end date 
START = 20140101
END = 20220520

# Make a data instance
pricevolume = KRXPriceDM(START, END)

# See available data and data module information
pricevolume.get_info()

# Download and load the data you want.
close_df = pricevolume.get_data("close")
close_df

```

# Wiki

# Contribution Guidlines

# Credit

This project is directly affected by a popular library, `FinanceDataReader` and `marcap`, both of which are from [FinanceData.KR](http://FinanceData.KR) repo.

# License
