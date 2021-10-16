# Pair-Trade-in-QQQ-and-ARKK
Both QQQ and ARKK are ETF that focuses on technology stocks in the US market. 
They have high correlation and a possible pair trading strategy could be formed using thses two ETF.

In the test_stationary.py file, I will test whether the return of QQQ and the return of ARKK could provide cotinegration property 
so we can develop a pair trade strategy on them.

In the backtest.py file, I will backtest the strategy using the result from test_stationary.py file. 
The cumulative return of the strategy from 2017 to 2021 is about 115%.
The daily Sharpe ratio is 1.50 and the winning ratio is 0.64.
