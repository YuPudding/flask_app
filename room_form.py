
from flask_wtf import FlaskForm
# flask_wtfからFlaskFormをimport
from flask_wtf import FlaskForm
from marshmallow import validates
from sqlalchemy import Integer
# wtformからフォームに必要なフィールドをimport
from wtforms import StringField, PasswordField, BooleanField, SubmitField,IntegerField
# wtformからフォームのバリデーションに必要な機能をimport
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo,NumberRange


class Room_Form(FlaskForm):
    roomname = StringField('部屋名',validators=[DataRequired()])
    uuid = StringField('UUID',validators=[DataRequired()])
    major = IntegerField('major',validators=[DataRequired(),NumberRange(0,100)])
    minor = IntegerField('minor',validators=[DataRequired(),NumberRange(0,100)])
