from flask_wtf import FlaskForm, Form
from wtforms import StringField, TextAreaField, SelectField, SubmitField, StringField, IntegerField, RadioField
from wtforms.validators import DataRequired
from wtforms.fields import DateField
# from wtforms import validators, ValidationError  

class TodoForm(FlaskForm):
	name = StringField("Name",validators=[DataRequired()])
	description = TextAreaField("Description",validators=[DataRequired()])
	completed = SelectField("Completed",choices=[("False","False"),("True","True")],validators=[DataRequired()])
	dt = DateField('DatePicker', format='%Y-%m-%d')
	submit = SubmitField("Add Todo")


class ContactForm(Form):  
   name = StringField("Candidate Name ",validators=[DataRequired()])  
   Gender = RadioField('Gender', choices = [('M','Male'),('F','Female')])  
   Address = TextAreaField("Address")  
      
   email = StringField("Email",validators=[DataRequired()])  
      
   Age = IntegerField("Age")  
   language = SelectField('Programming Languages', choices = [('java', 'Java'),('py', 'Python')])  
   
   submit = SubmitField("Submit") 