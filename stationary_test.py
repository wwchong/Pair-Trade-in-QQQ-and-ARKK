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

#merge the two dataset in order to make them align
merged = data.merge(data2, left_on=['date'], right_on=['date'], how='left',suffixes=[' QQQ', ' ARKK'])
merged.dropna(inplace=True)

#run regression on QQQ and ARKK's hourly returns
y = merged['change QQQ'].iloc[1:]
x = merged['change ARKK'].iloc[1:]
x = sm.add_constant(x)
model = sm.OLS(y,x,)
model = model.fit()
print(model.summary())

#calculate the residual using the coefficient estimated in the regression
merged['res'] = merged['change QQQ'] - 0.4969*merged['change ARKK']
plt.plot(merged['res'])

#run Augmented Dickey–Fuller test is to test the residual is white noise and print the test statistic
#the test statistic is about -17 so we can reject the null hypothesis that there is unit root
print("The test statistic of Augmented Dickey–Fuller test is " + str(ts.adfuller(merged['res'])[0]))

#run t test to check whether the mean of the residual is equal to 0
#the p-value is larger than 0.05 so we do not reject the null hypothesis that the mean is 0
a = st.ttest_1samp(a=merged['change QQQ'][1:]-0.4969*merged['change ARKK'][1:],popmean=0)
print("The p-value of the t-test is " + str(a.pvalue))

#Therefore, QQQ and ARKK show features of cointegration and we can develop a long-short strategy using them

