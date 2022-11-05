from flask.templating import render_template_string
from werkzeug.datastructures import RequestCacheControl
from werkzeug.utils import redirect
from application import app 
from flask import render_template,flash,request, url_for, redirect
from application import db
from .forms import TodoForm
from datetime import datetime
import pandas as pd
from bson import ObjectId


@app.route("/")
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
		return redirect("/")
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

		return redirect("/")
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
	return redirect("/")


