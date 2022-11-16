from tkinter import Text
import uuid
from flask_wtf import FlaskForm
# flask_wtfからFlaskFormをimport
from flask_wtf import FlaskForm
from sqlalchemy import Integer
# wtformからフォームに必要なフィールドをimport
from wtforms import StringField, PasswordField, BooleanField, SubmitField,IntegerField
# wtformからフォームのバリデーションに必要な機能をimport
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo,NumberRange


class Group_Form(FlaskForm):
    groupname= StringField('グループ名',validators=[DataRequired()])
