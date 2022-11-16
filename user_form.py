from tkinter import Text
import uuid
from click import password_option
from flask_wtf import FlaskForm
# flask_wtfからFlaskFormをimport
from flask_wtf import FlaskForm
from sqlalchemy import Integer, true


# wtformからフォームに必要なフィールドをimport
from wtforms import StringField, PasswordField, BooleanField, SubmitField,IntegerField,SelectField
# wtformからフォームのバリデーションに必要な機能をimport
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo,NumberRange




class Tuser_Form(FlaskForm):
    tusername = StringField("講師名",validators=[DataRequired()])
    password = StringField("パスワード",validators=[DataRequired()])


class User_Form(FlaskForm):
    username = StringField("ユーザ名",validators=[DataRequired()])
    groupid = SelectField("所属グループ") #リストボックス
    password = StringField("パスワード",validators=[DataRequired()])
