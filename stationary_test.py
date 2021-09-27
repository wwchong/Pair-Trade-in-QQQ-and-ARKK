import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy import stats as st
import statsmodels.tsa.stattools as ts

#read the data containing OHLC hourly data of QQQ and ARKK
data = pd.read_csv('QQQ.csv')
data2 = pd.read_csv('ARKK.csv')

#calculate the % change of the close price and set date as index
data['change'] = data['close'].pct_change()
data.set_index('date',inplace=True)
data2['change'] = data2['close'].pct_change()
data2.set_index('date',inplace=True)

