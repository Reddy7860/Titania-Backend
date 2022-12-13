from flask import Flask
from flask import Flask, flash, request,render_template,redirect
from client_data_display import *
import datetime
from werkzeug.utils import secure_filename
app = Flask(__name__,template_folder='template')


@app.route('/',methods =["POST","GET"])
def viewcredentials(): 
    dat,dat1,dat2,dat3,dat4=display_data("","")
    if request.method=="post":
        userid = request.form.get("cid")
        print(userid)
    else:
        userid = request.form.get("cid")
        dt = request.form.get("date")
            
            
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

if __name__ == "__main__":
    app.run(debug=True,port="9005")