import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#read the data containing OHLC hourly data of QQQ and ARKK
data = pd.read_csv('QQQ_5Y_5mins.csv')
data2 = pd.read_csv('ARKK_5Y_5mins.csv')

#change the date columne to datetime object
data['date'] = pd.to_datetime(data['date'])
data2['date'] = pd.to_datetime(data2['date'])

#calculate the % change of the close price and set date as index
data['change'] = data['close'].pct_change()
data.set_index('date',inplace=True)
data2['change'] = data2['close'].pct_change()
data2.set_index('date',inplace=True)

#merge the two dataset in order to make them align
merged = data.merge(data2, left_on=['date'], right_on=['date'], how='left',suffixes=[' QQQ', ' ARKK'])
merged.dropna(inplace=True)

#split the merged dataframe back to two dataframe to make them easier to handle
qqq = merged[['open QQQ','close QQQ','change QQQ']]
arkk = merged[['open ARKK','close ARKK','change ARKK']]
qqq.rename(columns={'open QQQ':'open','close QQQ':'close','change QQQ':'change'},inplace=True)
arkk.rename(columns={'open ARKK':'open','close ARKK':'close','change ARKK':'change'},inplace=True)

#Backtest
#when hourly change of QQQ - beta* hourly change of ARKK > threashold, we will sell QQQ and buy ARKK
#when hourly change of QQQ - beta* hourly change of ARKK < -threashold, we will buy QQQ and sell ARKK
#beta is the coefficient in the regression in the test_stationary.py file
#threashold is determined arbitrarily. A higher threashold may have higher winning rate but not necessarily higher return
j = 1
qqq_buy_price = 0
arkk_buy_price = 0
qqq_sell_price = 0
arkk_sell_price = 0
holding_arkk = 0
holding_qqq = 0
buy_qqq = False
buy_arkk = False
profit_history = []
profit = 0
principal = 10000
daily_principal = [10000]
daily_principal_dict = {arkk.index[0]:10000}
daily_return = [0]
trade_return = []
trade = 0
win = 0
beta = 0.4969
threshold = 0.008
mark = False
temp_principal = 0

while j<len(arkk)-1:
    if buy_arkk==False and buy_qqq==False:
        
        arkk_last_price = arkk['close'].iloc[j-2]
        qqq_last_price = qqq['close'].iloc[j-2]

        arkk_change = arkk['close'].iloc[j-1]/arkk_last_price-1
        qqq_change = qqq['close'].iloc[j-1]/qqq_last_price-1

        if qqq_change-arkk_change*beta>threshold:
            #short qqq, long arkk
            qqq_sell_price = qqq['open'].iloc[j]
            holding_qqq = int(principal/qqq_sell_price)
            arkk_buy_price = arkk['open'].iloc[j]
            holding_arkk = int(principal/arkk_buy_price)
            print("Time: " + str(arkk.index[j]))
            print("qqq sell price: "+str(qqq_sell_price))
            print("arkk buy price: "+str(arkk_buy_price))
            print("Holding qqq: " + str(holding_qqq))
            print("Holding arkk: " + str(holding_arkk))
            buy_arkk = True
            j += 1
            trade += 1
            continue
            
        elif qqq_change-arkk_change*beta<-threshold:
            #long qqq, short arkk
            qqq_buy_price = qqq['open'].iloc[j]
            holding_qqq = int(principal/qqq_buy_price)
            arkk_sell_price = arkk['open'].iloc[j]
            holding_arkk = int(principal/arkk_sell_price)
            print("Time: " + str(arkk.index[j]))
            print("qqq buy price: "+str(qqq_buy_price))
            print("arkk sell price: "+str(arkk_sell_price))
            print("Holding qqq: " + str(holding_qqq))
            print("Holding arkk: " + str(holding_arkk))
            buy_qqq = True
            j += 1
            trade += 1
            continue
    else:       
        arkk_last_price = arkk['close'].iloc[j-2]
        qqq_last_price = qqq['close'].iloc[j-2]
        arkk_change = arkk['close'].iloc[j-1]/arkk_last_price-1
        qqq_change = qqq['close'].iloc[j-1]/qqq_last_price-1
        
        if buy_arkk==True:
            current_profit = holding_qqq*(qqq_sell_price-qqq['close'].iloc[j-1]) + holding_arkk*(arkk['close'].iloc[j-1]-arkk_buy_price)
            if qqq_change-arkk_change*beta<=-threshold:
                qqq_buy_price = qqq['open'].iloc[j]
                arkk_sell_price = arkk['open'].iloc[j]
                profit = holding_qqq*(qqq_sell_price-qqq_buy_price) + holding_arkk*(arkk_sell_price-arkk_buy_price)
                if mark == True:
                    principal = temp_principal
                    mark = False
                profit_history.append(profit)
                trade_return.append(profit/principal)
                principal += profit
                print("qqq buy price: "+str(qqq_buy_price))
                print("arkk sell price: "+str(arkk_sell_price))
                buy_arkk = False
                j+= 1
                if profit>0:
                    win += 1
                holding_qqq = 0
                holding_arkk = 0
                continue
            
        elif buy_qqq==True:
            current_profit = holding_qqq*(qqq['close'].iloc[j-1]-qqq_buy_price)+ holding_arkk*(arkk_sell_price-arkk['close'].iloc[j-1])
            if qqq_change-arkk_change*beta>=threshold:
                qqq_sell_price = qqq['open'].iloc[j]
                arkk_buy_price = arkk['open'].iloc[j]
                profit = holding_qqq*(qqq_sell_price-qqq_buy_price) + holding_arkk*(arkk_sell_price-arkk_buy_price)
                if mark == True:
                    principal = temp_principal
                    mark = False
                profit_history.append(profit)
                trade_return.append(profit/principal)
                principal += profit
                print("qqq sell price: "+str(qqq_sell_price))
                print("arkk buy price: "+str(arkk_buy_price))
                buy_qqq = False
                holding_qqq = 0
                holding_arkk = 0
                j += 1
                if profit>0:
                    win += 1
                holding_qqq = 0
                holding_arkk = 0
                continue
    if qqq.index[j].hour == 14:
        if buy_qqq == True:
            if mark == False:
                temp_principal = principal
                mark = True

            principal = temp_principal
            principal += holding_qqq*(qqq['close'].iloc[j] - qqq_buy_price)
            principal += holding_arkk*(arkk_sell_price-arkk['close'].iloc[j])

        elif buy_arkk == True:
            if mark == False:
                temp_principal = principal
                mark = True
            principal = temp_principal
            principal += holding_qqq*(qqq_sell_price - qqq['close'].iloc[j])
            principal += holding_arkk*(arkk['close'].iloc[j] - arkk_buy_price)


        daily_principal_dict[arkk.index[j]] = principal
        daily_principal.append(principal)
        daily_return.append(daily_principal[-1]/daily_principal[-2]-1)
    
    j += 1
    
#liquidate all the position at the end of the backtest
if buy_arkk == True:
    qqq_buy_price = qqq['close'].iloc[-1]
    arkk_sell_price = arkk['close'].iloc[-1]
    profit = holding_qqq*(qqq_sell_price-qqq_buy_price) + holding_arkk*(arkk_sell_price-arkk_buy_price)
    profit_history.append(profit)
    trade_return.append(profit/principal)
    principal += profit
    print("qqq buy price: "+str(qqq_buy_price))
    print("arkk sell price: "+str(arkk_sell_price))
    buy_arkk = False
    if profit>0:
        win += 1
    holding_qqq = 0
    holding_arkk = 0
    daily_principal_dict[arkk.index[j]] = principal
    daily_principal.append(principal)
    daily_return.append(daily_principal[-1]/daily_principal[-2]-1)
        
elif buy_qqq == True:
    qqq_sell_price = qqq['close'].iloc[-1]
    arkk_buy_price = arkk['close'].iloc[-1]
    profit = holding_qqq*(qqq_sell_price-qqq_buy_price) + holding_arkk*(arkk_sell_price-arkk_buy_price)
    profit_history.append(profit)
    trade_return.append(profit/principal)
    principal += profit
    print("qqq sell price: "+str(qqq_sell_price))
    print("arkk buy price: "+str(arkk_buy_price))
    buy_qqq = False
    if profit>0:
        win += 1
    holding_qqq = 0
    holding_arkk = 0
    daily_principal_dict[arkk.index[j]] = principal
    daily_principal.append(principal)
    daily_return.append(daily_principal[-1]/daily_principal[-2]-1)
 
#Return of the strategy 
print("Cumulative Return: " + str(principal/10000-1))

#Sharpe ratio of the strategy
daily_principal_dataframe = pd.DataFrame({'principal':daily_principal_dict.values()},index=daily_principal_dict.keys())
daily_principal_dataframe['change'] = daily_principal_dataframe['principal'].pct_change()
daily_principal_dataframe['Cum_return'] = daily_principal_dataframe['change'].add(1).cumprod().sub(1)
print("Strategy's Sharpe Ratio: " + str(daily_principal_dataframe['Cum_return'].iloc[-1]/daily_principal_dataframe['Cum_return'].std()))

#winning rate of the strategy
print("Winning rate: " + str(win/trade))
    
            
