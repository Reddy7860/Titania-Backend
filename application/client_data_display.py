import pandas as pd
from datetime import datetime,timedelta
from pandasql import sqldf
import math
from pandas.io.json import json_normalize
import json
import numpy as np
import time
import datetime as dt
from pytz import timezone

from sqlalchemy import create_engine
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import ssl
import certifi
from urllib.request import urlopen




def display_data(client_id,date_inpt):



    # request = "https://google.com"
    # urlopen(request, context=ssl.create_default_context(cafile=certifi.where()))


    pd.set_option('display.max_columns', None)

    start_time = datetime.now(timezone("Asia/Kolkata")) 
    print("Script execution started")
    print(start_time)

    server_api = ServerApi('1')

    client = MongoClient("mongodb+srv://Titania:Mahadev@cluster0.zq3w2cn.mongodb.net/titania_trading?ssl=true&ssl_cert_reqs=CERT_NONE", server_api=server_api, tlsCAFile=certifi.where())
    db = client["titania_trading"]

    client_details = db["client_details"].find({'client_id':{'$in' :['J95213','S1604557','G304915','K256027','M591295','M181705']}})
    # client_details = db["client_details"].find({'client_id':{'$in' :['J95213','M591295','M181705']}})
    client_data =  pd.DataFrame(list(client_details))

    #print(client_data)


    ################################
    ## Input Parameters 
    ################################
    if date_inpt=="":
        date_input = "2022-12-14"
    else:
        date_input=date_inpt
    final_open_data = pd.DataFrame()
    final_stoploss_data = pd.DataFrame()
    final_position_data = pd.DataFrame()
    final_completed_orders = pd.DataFrame()
    final_closed_positions = pd.DataFrame()

    for i in range(0,len(client_data)):
        user_id = str(client_data.loc[i,"client_id"])
        print("Running script for ",str(client_data.loc[i,"client_name"])) 

    #     previous_orders = pd.DataFrame()
        
    #     if (os.path.isfile("/home/sjonnal3/Hate_Speech_Detection/Trading_Application/Orders_Data/"+str(client_data.loc[i,"client_id"])+"/Updated_Targets/IV_Based_" + date_input +".csv")):
    #         print("File Exists")
    #         try:
    #             previous_orders = pd.read_csv("/home/sjonnal3/Hate_Speech_Detection/Trading_Application/Orders_Data/"+str(client_data.loc[i,"client_id"])+"/Updated_Targets/IV_Based_" + date_input +".csv")
    #         except e:
    #             previous_orders = pd.read_csv("/home/sjonnal3/Hate_Speech_Detection/Trading_Application/Orders_Data/"+str(client_data.loc[i,"client_id"])+"/Updated_Targets/" + date_input +".csv")
    #     else:
    #         print("Previous Orders is Null")
    #         previous_orders = pd.DataFrame(columns = ['symboltoken', 'symbolname', 'instrumenttype','priceden','pricenum','genden','gennum','precision','multiplier','boardlotsize','exchange','producttype','tradingsymbol','symbolgroup','strikeprice','optiontype','expirydate','lotsize','cfbuyqty','cfsellqty','cfbuyamount','cfsellamount','buyavgprice','sellavgprice','avgnetprice','netvalue','netqty','totalbuyvalue','totalsellvalue','cfbuyavgprice','cfsellavgprice','totalbuyavgprice','totalsellavgprice','netprice','buyqty','sellqty','buyamount','sellamount','pnl','realised','unrealised','ltp','close','target_order_id','stop_loss_order_id','final_order_id','cancel_order_id','max_profit_percent','min_profit_percent','current_stoploss_percent','current_prob','implied_volatility_time','implied_volatility','IV_Stoploss','IV_Target'])
            
            
        order_data = db["Order_Data"].find({'Client_id':{'$in' :[str(client_data.loc[i,"client_id"])]},'execution_date':str(date_input)}).sort("updatetime", -1)
        position_data = db["Position_Data"].find({'Client_id':{'$in' :[str(client_data.loc[i,"client_id"])]},'execution_date':str(date_input)})
        
        order_data =  pd.DataFrame(list(order_data))
        position_data =  pd.DataFrame(list(position_data))
        
        print("Order Data")
    #     print(order_data)
        print(len(position_data))
    #     print("Position Data")
    #     print(position_data)
        
        pysqldf = lambda q: sqldf(q, globals())
        
        if len(order_data) > 0:
            open_positions = order_data.loc[order_data['status'] == "open",]
            stoploss_pending = order_data.loc[order_data['status'] == "trigger pending",]
            completed_orders = order_data.loc[order_data['status'] == "complete",]

            if len(open_positions) > 0 :
                open_positions.reset_index(inplace=True,drop=True)
                open_positions['Client_id'] = str(client_data.loc[i,"client_id"])
                final_open_data = final_open_data.append(open_positions)
            
            if len(stoploss_pending) > 0 :
                stoploss_pending.reset_index(inplace=True,drop=True)
                stoploss_pending['Client_id'] = str(client_data.loc[i,"client_id"])
                final_stoploss_data = final_stoploss_data.append(stoploss_pending)
                
            if len(completed_orders) > 0 :
                print(completed_orders.columns)
                completed_orders.reset_index(inplace=True,drop=True)
                completed_orders['Client_id'] = str(client_data.loc[i,"client_id"])
                final_completed_orders = final_completed_orders.append(completed_orders)
                
        if len(position_data) > 0:
            position_data['Client_id'] = str(client_data.loc[i,"client_id"])
            
            closed_orders = position_data.loc[position_data['netprice'] == '0.00',]
            pending_positions = position_data.loc[position_data['netprice'] != '0.00',]
            
            if len(closed_orders) > 0:
                final_closed_positions = final_closed_positions.append(closed_orders)
                
            if len(pending_positions) > 0:
                final_position_data = final_position_data.append(pending_positions)
            
            
      
    print("-----------------------")  
    #print(final_closed_positions.columns)
    fpd=[]
    fcp=[]
    fsd=[]
    fod=[]
    fco=[]
    if len(final_position_data) > 0:
        final_position_data=final_position_data[['Client_id','tradingsymbol','producttype','netqty','lotsize','netprice','pnl','ltp','close']]
        fpd.append(final_position_data)
    else:
        fpd.append(["No"," pending", "orders" ,"to"," close","","","","",""])
        
        
        
    if len(final_closed_positions) > 0:
        final_closed_positions = final_closed_positions[['Client_id','tradingsymbol','producttype','netqty','lotsize','netprice','pnl','ltp','close']]
        fcp.append(final_closed_positions)
    else:
        fcp.append(["No", "Closed ","Positions"])
        
        
    if len(final_stoploss_data) > 0:
        final_stoploss_data = final_stoploss_data[['Client_id','tradingsymbol','producttype','price','transactiontype','quantity','lotsize','symboltoken','instrumenttype','orderid']]
        fsd.append(final_stoploss_data)
    else:
        fsd.append(["No"," Stoploss"," Positions"])

    if len(final_open_data) > 0:
        final_open_data = final_open_data[['Client_id','tradingsymbol','producttype','price','transactiontype','quantity','lotsize','symboltoken','instrumenttype','orderid']]
        fod.append(final_open_data)
    else:
        fod.append(["No", "Open Orders", "to", "Execute"])
        
        
    if len(final_completed_orders) > 0:
        final_completed_orders = final_completed_orders[['Client_id','tradingsymbol','producttype','price','transactiontype','quantity','lotsize','symboltoken','instrumenttype','orderid']]
        
        fco.append(final_completed_orders)
        
    else:
        fco.append(["No Orders for now"])
    if client_id=="":
        return fco[0],fpd[0],fcp[0],fsd[0],fod[0]
        # if type(fpd[0])==list or type(fcp[0])==list or type(fsd[0])==list or type(fod[0]) or type(fco[0]):
        #     return fco[0],fpd[0],fcp[0],fsd[0],fod[0]
    else:
        final_completed_orders=fco[0][fco[0]['Client_id']==client_id]
        #     final_open_data=fod[0][fod[0]['Client_id']==client_id]
        #     final_stoploss_data=fsd[0][fsd[0]['Client_id']==client_id]
        #     final_closed_positions=fcp[0][fcp[0]['Client_id']==client_id]
        #     final_position_data=fpd[0][fpd['Client_id']==client_id]
            
            #return final_completed_orders,final_position_data,final_closed_positions,final_stoploss_data,final_open_data
            #return fco[0],fpd[0],fcp[0],fsd[0],fod[0]
        #print(type(fco[0]))
        return final_completed_orders
    # if len(final_completed_orders) > 0 or len(final_position_data)>0 or len(final_closed_positions)>0 or len(final_stoploss_data)>0 or len(final_open_data)>0:
    #     if client_id=="":
    #         final_completed_orders = final_completed_orders[['Client_id','tradingsymbol','producttype','price','transactiontype','quantity','lotsize','symboltoken','instrumenttype','orderid']]
        
    #         final_open_data = final_open_data[['Client_id','tradingsymbol','producttype','price','transactiontype','quantity','lotsize','symboltoken','instrumenttype','orderid']]
    #         final_stoploss_data = final_stoploss_data[['Client_id','tradingsymbol','producttype','price','transactiontype','quantity','lotsize','symboltoken','instrumenttype','orderid']]
    #         final_closed_positions = final_closed_positions[['Client_id','tradingsymbol','producttype','netqty','lotsize','netprice','pnl','ltp','close']]
    #         final_position_data=final_position_data[['Client_id','tradingsymbol','producttype','netqty','lotsize','netprice','pnl','ltp','close']]
    #         return final_completed_orders,final_position_data,final_closed_positions,final_stoploss_data,final_open_data
            
    #     else:

    #         final_completed_orders = final_completed_orders[['Client_id','tradingsymbol','producttype','price','transactiontype','quantity','lotsize','symboltoken','instrumenttype','orderid']]
    #         final_open_data = final_open_data[['Client_id','tradingsymbol','producttype','price','transactiontype','quantity','lotsize','symboltoken','instrumenttype','orderid']]
    #         final_stoploss_data = final_stoploss_data[['Client_id','tradingsymbol','producttype','price','transactiontype','quantity','lotsize','symboltoken','instrumenttype','orderid']]
    #         final_closed_positions = final_closed_positions[['Client_id','tradingsymbol','producttype','netqty','lotsize','netprice','pnl','ltp','close']]
    #         final_position_data=final_position_data[['Client_id','tradingsymbol','producttype','netqty','lotsize','netprice','pnl','ltp','close']]
      
    #         final_completed_orders=final_completed_orders[final_completed_orders['Client_id']==client_id]
    #         final_open_data=final_open_data[final_open_data['Client_id']==client_id]
    #         final_stoploss_data=final_stoploss_data[final_stoploss_data['Client_id']==client_id]
    #         final_closed_positions=final_closed_positions[final_closed_positions['Client_id']==client_id]
    #         final_position_data=final_position_data[final_position_data['Client_id']==client_id]
            
    #         print(final_open_data)
    #         return final_completed_orders,final_position_data,final_closed_positions,final_stoploss_data,final_open_data

        
    # else:

    #     final_completed_orders=[["No Data is Found"]]
    #     final_open_data=[["No Data is Found"]]
    #     final_stoploss_data=[["No Data is Found"]]
    #     final_closed_positions=[["No Data is Found"]]
    #     final_position_data=[["No Data is Found"]]
            
    #     print(final_open_data)
    #     return final_completed_orders,final_position_data,final_closed_positions,final_stoploss_data,final_open_data
#display_data("","")