from flask.templating import render_template_string
from werkzeug.datastructures import RequestCacheControl
from werkzeug.utils import redirect
from application import app 
from flask import render_template,flash,request, url_for, redirect,Flask,redirect, Response, session,jsonify
# from wtforms.fields import DateField,DateTimeField 
# from wtforms.fields import DateField
from wtforms.fields import DateField,DateTimeField 

# from flask_wtf import Form
from flask_wtf import FlaskForm, Form

from application import db
from .forms import TodoForm, ContactForm
from .get_VIP_graph import get_graph
from .get_Global_Data import get_global_market
from .get_s_and_p_Data import get_s_and_p_market



from datetime import datetime
import pandas as pd
from bson import ObjectId
from flask_table import Table, Col

import pandas as pd
from pandas.io import gbq
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import pandas_gbq

from wtforms.validators import DataRequired
from wtforms import validators, SubmitField

from flask import Flask
from .client_data_display import *
import datetime
from werkzeug.utils import secure_filename

import plotly
import plotly.express as px

# import mysql.connector as mysql
# import pymysql

# from sqlalchemy.engine import result
# import sqlalchemy
# from sqlalchemy import create_engine, MetaData,\
# Table, Column, Numeric, Integer, VARCHAR, update, delete


# from sqlalchemy import create_engine

# import certifi
# import ssl
# from urllib.request import build_opener, Request, ProxyHandler, HTTPSHandler
# import seaborn as sns


# context=ssl.create_default_context(cafile=certifi.where())
# https_handler = HTTPSHandler(context=context)
# opener = build_opener(https_handler, ProxyHandler(hcaptcha_settings.PROXIES))
# iris = sns.load_dataset('iris')
# template_dir = os.path.abspath('templates')




class InfoForm(FlaskForm):
    startdate = DateField('Start Date', format='%Y-%m-%d', validators=(validators.DataRequired(),))
    # enddate = DateField('End Date', format='%Y-%m-%d', validators=(validators.DataRequired(),))
    submit = SubmitField('Submit')

@app.route('/datepicker', methods=['GET','POST'])
def index():
    form = InfoForm()
    if form.validate_on_submit():
        session['startdate'] = form.startdate.data
        # session['enddate'] = form.enddate.data
        return redirect('algotrades')
    return render_template('index.html', form=form)

@app.route('/date', methods=['GET','POST'])
def date():
    startdate = session['startdate']
    # remove the GMT
    startdate = startdate[:-4]
    print(startdate)
    startdate = datetime.strptime(startdate,'%a, %d %b %Y %H:%M:%S').date()
    print(startdate)
    # enddate = session['enddate']
    return render_template('date.html')


@app.route('/algotrades',methods=['POST','GET'])
def algo_trade():
	startdate = session['startdate']
	startdate = startdate[:-4]
	startdate = datetime.strptime(startdate,'%a, %d %b %Y %H:%M:%S').date()
	print(startdate)

	# sql = """
	# SELECT max(Execution_Date) FROM `reddy000-c898c.Titania_Dataset.Stocks_data_5_minutes`
	# """
	sql = "select * from `reddy000-c898c.Titania_Dataset.algo_orders_place_data` where execution_date = '"+str(startdate)+"' order by Datetime desc"
	# sql = """
	# select * from `reddy000-c898c.Titania_Dataset.algo_orders_place_data` 
	# where execution_date = '2022-11-04'
	# order by Datetime desc
	# """
	algo_orders = pandas_gbq.read_gbq(sql, project_id='reddy000-c898c')

	sql = "select * from `reddy000-c898c.Titania_Dataset.algo_order_data` where execution_date = '"+str(startdate)+"'"

	# sql = """
	# select * from `reddy000-c898c.Titania_Dataset.algo_order_data` 
	# where execution_date = '2022-11-04'
	# """
	order_data = pandas_gbq.read_gbq(sql, project_id='reddy000-c898c')

	print(order_data.tail(5))

	sql = "select * from `reddy000-c898c.Titania_Dataset.algo_position_data` where execution_date = '"+str(startdate)+"'"

	# sql = """
	# select * from `reddy000-c898c.Titania_Dataset.algo_position_data` 
	# where execution_date = '2022-11-04'
	# """
	position_data = pandas_gbq.read_gbq(sql, project_id='reddy000-c898c')

	print(position_data.head(5))

	# engine = create_engine("mysql+pymysql://root:Mahadev_143@localhost/titania_trading")
	# print(engine)

	# con = mysql.connect(user='root', password='Mahadev_143', database='titania_trading')
	# cursor = con.cursor()

	# order_data = '''
	# select * from order_data
	# where Execution_date = '2022-11-04'
	# order by Execution_date desc
	# '''

	# order_data = pd.read_sql(order_data,con=engine)


	# position_data = '''
	# select * from position_data
	# where Execution_Date = '2022-11-04'
	# '''
	# position_data = pd.read_sql(position_data,con=engine)


	order_data['orderid'] = order_data['orderid'].astype(str)
	algo_orders['order_id'] = algo_orders['order_id'].astype(str)

	combined_data = algo_orders.merge(order_data, left_on='order_id', right_on='orderid', how='left')


	missed_orders = combined_data['orderstatus'].isna().sum()
	rejected_orders = combined_data.loc[combined_data['orderstatus']=="rejected"]
	completed_orders = combined_data.loc[combined_data['orderstatus']=="complete"]
	cancelled_orders = combined_data.loc[combined_data['orderstatus']=="cancelled"]


	completed_orders.reset_index(inplace=True,drop=True)


	completed_orders.loc[completed_orders['Client_id'] == 'J95213']

	completed_orders = completed_orders[['Client_id','Strategy','Stock','Signal','Value','buy_probability','sell_probability','StopLoss','Target','Qty','Strike_Buy_Price',"premium_StopLoss","premium_Target","lotsize_x","historic_profit","current_script","token","execution_date","order_id","averageprice","updatetime","exchorderupdatetime"]]

	print(completed_orders)
	print(completed_orders.columns)

	for ind in completed_orders.index:
		print(completed_orders['Client_id'][ind], completed_orders['Strategy'][ind])

	return render_template("/completed_orders.html", value=completed_orders)

@app.route("/home")
def get_todos():
	todos = []
	# data = db.todo_flask.find({}).sort([('date_completed', -1)])
	# data =  pd.DataFrame(list(data))
	# print(data)
	# print(db.todo_flask.find({}).sort("date_completed", -1))

	for todo in db.todo_flask.find().sort("date_completed", -1):
		todo["_id"] = str(todo["_id"])
		todo["date_completed"] = todo["date_completed"].strftime('%b %d %Y')
		todos.append(todo)
	return render_template("view_todos.html",title = "Titania Trading and Research",todos=todos)

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        print(request.form['username'])
        print(request.form['password'])
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect('/home')
    return render_template('login.html', error=error)

# @app.route("/orders_preview",methods=["POST","GET"])
# def orders_preview():
# 	clients = []

# 	for client in db.client_details.find({}):
# 		clients.append(str(client['client_id']))

# 	print(clients)

# 	return render_template("get_object.html", clients=clients)

	# daily_orders = []
	# for order in db.orders_raw_data.find().sort("Datetime", -1):
	# 	order["_id"] = str(order["_id"])
	# 	order["Strategy"] = str(order["Strategy"])
	# 	order["Stock"] = str(order["Stock"])
	# 	order["Signal"] = str(order["Signal"])
	# 	# order["Datetime"] = order["Datetime"].strftime('%d %m %Y %H:%M:%S')
	# 	order["Datetime"] = str(order["Datetime"])
	# 	order["buy_probability"] = str(order["buy_probability"])
	# 	order["sell_probability"] = str(order["sell_probability"])
		
	# 	daily_orders.append(order)

	# # print(daily_orders)
	# print(daily_orders[0])


	# return render_template('orders_preview.html', value=daily_orders)


@app.route('/orders_preview',methods =["POST","GET"])
def orders_preview(): 
    dat,dat1,dat2,dat3,dat4=display_data("","")
    if request.method=="post":
        userid = request.form.get("cid")
        print(userid)
        # search_text = request.form['query']
    else:
        userid = request.form.get("cid")
        dt = request.form.get("date")

        print("The selected date : ")
        print(dt)
            
            
        if userid:
            data=display_data(userid,dt)
                

            data=data.values.tolist()
            

            name=dat['Client_id'].unique()
            return render_template('view.html',data=data,name=name)
        else:
            data,data1,data2,data3,data4=display_data("","")
            name=dat['Client_id'].unique()
            if  type(data1)==list and type(data2)==list and type(data3)==list and type(data4)==list:
                
                data1=data1
                data2=data2
                data3=data3
                data4=data4
            else:
                data=data.values.tolist()
                #data1=data1.values.tolist()
                data2=data2.values.tolist()
                #data2=data3.values.tolist()
                #data4=data4.values.tolist()
                        
            return render_template('view.html',data=data,data1=[data1],data2=data2,data3=[data3],data4=[data4],name=name)

# @app.route("/fetch_orders",methods=["POST","GET"])
# def fetch_orders():
# 	print("inside fetch orders")
# 	daily_orders = []

# 	# client_details = db["client_details"].find({'client_id':{'$in' :['J95213','S1604557','G304915','K256027','M591295','M181705']}})
# 	# client_details = db["client_details"].find({'client_id':{'$in' :['J95213','M591295','M181705']}})
# 	# client_data =  pd.DataFrame(list(client_details))



# 	if request.method == 'POST':

# 		print("Post method")
# 		# query = request.form['query']

# 		query = ''
# 		# draw = request.form['draw'] 
# 		row = int(request.form['start'])
# 		rowperpage = int(request.form['length'])
# 		searchValue = request.form["search[value]"]
# 		#print(draw)
# 		print(row)
# 		print(rowperpage)

# 		# print(query)
# 		if query == '':
# 			for order in db.algo_orders_place_data.find().sort("Datetime", -1):
# 				order["_id"] = str(order["_id"])
# 				order["Strategy"] = str(order["Strategy"])
# 				order["Stock"] = str(order["Stock"])
# 				order["Signal"] = str(order["Signal"])
# 				# order["Datetime"] = order["Datetime"].strftime('%d %m %Y %H:%M:%S')
# 				order["Datetime"] = str(order["Datetime"])
# 				order["buy_probability"] = str(order["buy_probability"])
# 				order["sell_probability"] = str(order["sell_probability"])
				
# 				daily_orders.append(order)
# 		else:
# 			search_text = request.form['query']
# 			# print(search_text)
# 			for order in db.algo_orders_place_data.find({"client_id":str(search_text)}).sort("Datetime", -1):
# 				order["_id"] = str(order["_id"])
# 				order["Strategy"] = str(order["Strategy"])
# 				order["Stock"] = str(order["Stock"])
# 				order["Signal"] = str(order["Signal"])
# 				# order["Datetime"] = order["Datetime"].strftime('%d %m %Y %H:%M:%S')
# 				order["Datetime"] = str(order["Datetime"])
# 				order["buy_probability"] = str(order["buy_probability"])
# 				order["sell_probability"] = str(order["sell_probability"])
				
# 				daily_orders.append(order)
# 	# print(daily_orders)
# 	# return {'data': [order for order in daily_orders]}
# 	# return jsonify({'htmlresponse': render_template('response.html', daily_orders=daily_orders)})
# 	# return render_template('response.html', value=daily_orders)

# 	# client_details = db["client_details"].find({'client_id':{'$in' :['J95213','S1604557','G304915','K256027','M591295','M181705']}})
# 	client_details = db["client_details"].find({'client_id':{'$in' :['J95213','M591295','M181705']}})
# 	client_data =  pd.DataFrame(list(client_details))

# 	date_input = "2022-12-05"

# 	final_open_data = pd.DataFrame()
# 	final_position_data = pd.DataFrame()

# 	for i in range(0,len(client_data)):
# 	    user_id = str(client_data.loc[i,"client_id"])
# 	    print("Running script for ",str(client_data.loc[i,"client_name"])) 
# 	    order_data = db["Order_Data"].find({'Client_id':{'$in' :[str(client_data.loc[i,"client_id"])]},'execution_date':str(date_input)})
# 	    position_data = db["Position_Data"].find({'Client_id':{'$in' :[str(client_data.loc[i,"client_id"])]},'execution_date':str(date_input)})
	    
# 	    order_data =  pd.DataFrame(list(order_data))
# 	    position_data =  pd.DataFrame(list(position_data))
	    
# 	#     print("Order Data")
# 	#     print(order_data)
# 	# #     print(len(position_data))
# 	#     print("Position Data")
# 	#     print(position_data)
	    
# 	    pysqldf = lambda q: sqldf(q, globals())
	    
# 	    if len(order_data) > 0:
# 	        open_positions = order_data.loc[order_data['status'] == "open",]

# 	        if len(open_positions) > 0 :
# 	            open_positions.reset_index(inplace=True,drop=True)
# 	            open_positions['Client_id'] = str(client_data.loc[i,"client_id"])
# 	            final_open_data = final_open_data.append(open_positions)
	            
# 	    if len(position_data) > 0:
# 	        final_position_data['Client_id'] = str(client_data.loc[i,"client_id"])
# 	        final_position_data = final_position_data.append(position_data)

# 	# print(final_open_data)
# 	# print(final_position_data)

# 	# print(final_open_data.columns)
# 	# print(final_position_data.columns)

# 	# final_open_data = final_open_data[['Client_id','tradingsymbol','producttype','netqty','lotsize','netprice','pnl','ltp','close']]
# 	# final_position_data = final_position_data[['Client_id','tradingsymbol','producttype','price','transactiontype','quantity','lotsize','symboltoken','instrumenttype','orderid']]


# 	# print(daily_orders)

# 	# data = []
# 	# for row in daily_orders:
# 	# 	data.append({
# 	# 	    'Strategy': row['Strategy'],
# 	# 	    'Stock': row['Stock'],
# 	# 	    'Signal': row['Signal'],
# 	# 	    'Datetime': row['Datetime'],
# 	# 	    'buy_probability': row['buy_probability'],
# 	# 	    'sell_probability': row['sell_probability'],
# 	# 	    'current_script': row['current_script'],
# 	# 	    'order_id': row['order_id'],
# 	# 	})

# 	# response = {
#  #                'iTotalRecords': 100,
#  #                'iTotalDisplayRecords': 100,
#  #                'aaData': data,
#  #            }

# 	# print("Response")
# 	# print(response)
# 	# return jsonify(response)
# 	return jsonify({'htmlresponse': render_template('response.html', daily_orders=daily_orders,final_open_data = final_open_data,final_position_data = final_position_data )})

@app.route("/ai_trading",methods=["GET"])
def ai_trading():
    return render_template('ai_trading_latest.html')

@app.route('/nasdaq_data')
def nasdaq_data():
    return jsonify(get_global_market())

@app.route('/s_and_p_data')
def s_and_p_data():
    return jsonify(get_s_and_p_market())



    
# def ai_trading():


# 	return jsonify(get_global_market())

	# df = pd.DataFrame({
 #      'Fruit': ['Apples', 'Oranges', 'Bananas', 'Apples', 'Oranges','Bananas'],
 #      'Amount': [4, 1, 2, 2, 4, 5],
 #      'City': ['SF', 'SF', 'SF', 'Montreal', 'Montreal', 'Montreal']
 #   })
	# fig = px.bar(df, x='Fruit', y='Amount', color='City', barmode='group')
	# graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	# return render_template('notdash.html', graphJSON=graphJSON)


	# daily_orders = []
	# for order in db.orders_raw_data.find().sort("Datetime", -1):
	# 	order["_id"] = str(order["_id"])
	# 	order["Strategy"] = str(order["Strategy"])
	# 	order["Stock"] = str(order["Stock"])
	# 	order["Signal"] = str(order["Signal"])
	# 	# order["Datetime"] = order["Datetime"].strftime('%d %m %Y %H:%M:%S')
	# 	order["Datetime"] = str(order["Datetime"])
	# 	order["buy_probability"] = str(order["buy_probability"])
	# 	order["sell_probability"] = str(order["sell_probability"])
		
	# 	daily_orders.append(order)

	# # print(daily_orders)
	# print(daily_orders[0])


	# return render_template('ai_trading.html', value=daily_orders)

@app.route("/technical_indicators",methods=["GET"])
def technical_preview():
	technical_indicators = []
	for technical in db.technical_indicator_5_minutes.find().sort("Datetime", -1):
		technical["_id"] = str(technical["_id"])
		# order["Strategy"] = str(order["Strategy"])
		# order["Stock"] = str(order["Stock"])
		# order["Signal"] = str(order["Signal"])
		# # order["Datetime"] = order["Datetime"].strftime('%d %m %Y %H:%M:%S')
		# order["Datetime"] = str(order["Datetime"])
		# order["buy_probability"] = str(order["buy_probability"])
		# order["sell_probability"] = str(order["sell_probability"])
		
		technical_indicators.append(technical)

	# print(daily_orders)
	print(technical_indicators[0])


	return render_template('technical_preview.html', value=technical_indicators)

@app.route('/technical_chart')
def technical_chart():
    return jsonify(get_global_market())

@app.route("/options_signals",methods=["GET"])
def options_signals_preview():
	options_signals = []
	for signal in db.options_signals.find().sort("Datetime", -1):
		signal["_id"] = str(signal["_id"])
		# order["Strategy"] = str(order["Strategy"])
		# order["Stock"] = str(order["Stock"])
		# order["Signal"] = str(order["Signal"])
		# # order["Datetime"] = order["Datetime"].strftime('%d %m %Y %H:%M:%S')
		# order["Datetime"] = str(order["Datetime"])
		# order["buy_probability"] = str(order["buy_probability"])
		# order["sell_probability"] = str(order["sell_probability"])
		
		options_signals.append(signal)

	# print(daily_orders)
	print(options_signals[0])


	return render_template('options_signals.html', value=options_signals)




# @app.route('/datepicker', methods=['POST','GET'])
# def hello_world():
#     return render_template('datepicker_example.html')

@app.route('/supp_res')
def supp_res():
    return jsonify(get_graph())

@app.route('/support_and_resistance')
def support_and_resistance():
	return render_template('support_and_resistance.html')


@app.route('/fig')
def fig():
    return jsonify(get_graph())


@app.route('/fighome')
@app.route('/figurehome')
def home():
    return render_template('main.html')

@app.route('/admin')
def hello_admin():
	return 'Hello Admin'

@app.route('/guest/<guest>')
def hello_guest(guest):
	return 'Hello %s as Guest' % guest

@app.route('/user/<name>')
def hello_user(name):
   if name =='admin':
      return redirect(url_for('hello_admin'))
   else:
      return redirect(url_for('hello_guest',guest = name))


# @app.route('/contact', methods = ['GET', 'POST'])  
# def contact():  
#    form = ContactForm()  
#    if form.validate() == False:  
#       flash('All fields are required.')  
#    return render_template('contact.html', form = form) 

# @app.route('/success',methods = ['GET','POST'])  
# def success():  
#    return render_template("success.html") 

@app.route("/add_todo", methods = ["POST","GET"])
def add_todo():
	if request.method == "POST":
		form = TodoForm(request.form)
		todo_name = form.name.data
		todo_description = form.description.data
		completed = form.completed.data

		db.todo_flask.insert_one({
			"name" : todo_name,
			"description": todo_description,
			"completed":completed,
			"date_completed":datetime.now()
			})
		flash("Todo successfully inserted","success")
		return redirect("/home")
	else:
		form = TodoForm()
	return render_template("add_todo.html",form = form)

@app.route('/update_todo/<id>',methods=["POST","GET"])
def update_todo(id):
	if request.method == "POST":
		form = TodoForm(request.form)
		todo_name = form.name.data
		todo_description = form.description.data
		completed = form.completed.data

		db.todo_flask.find_one_and_update({"_id":ObjectId(id)},{"$set":{
			"name" : todo_name,
			"description": todo_description,
			"completed":completed,
			"date_completed":datetime.now()
		}})

		flash("Todo successfully update","success")

		return redirect("/home")
	else:
		form = TodoForm()

		todo = db.todo_flask.find_one_or_404({"_id": ObjectId(id)})

		form.name.data = todo.get("name",None)
		form.description.data = todo.get("description",None)
		form.completed.data = todo.get("completed",None)

	return render_template("add_todo.html",form = form)


@app.route("/delete_todo/<id>")
def delete_todo(id):
	db.todo_flask.find_one_and_delete({"_id":ObjectId(id)})
	flash("Todo deleted","success")
	return redirect("/home")


