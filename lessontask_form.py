import imp
from importlib.machinery import PathFinder
from flask_wtf import FlaskForm
# flask_wtfからFlaskFormをimport
from flask_wtf import FlaskForm
from sqlalchemy import Time, false
# wtformからフォームに必要なフィールドをimport
from wtforms import StringField, PasswordField, BooleanField, SubmitField,IntegerField,DateField,DateTimeField,SelectField,TimeField
# wtformからフォームのバリデーションに必要な機能をimport
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo,NumberRange
from datetime import datetime,time





class LessonTask_Form(FlaskForm):

    #lessontaskid  オートインクリメント

    lessontaskdate = DateField("年月日",validators=[DataRequired()])
    periode = IntegerField("限目",validators=[DataRequired(),NumberRange(1,4)])

    #lessonid = SelectField() 遷移画面からの値を取得
    roomid = SelectField("部屋")

    sutime = TimeField("開始時刻",validators=[DataRequired()])
    mistime = TimeField("遅刻時刻",validators=[DataRequired()])
    notime = TimeField("欠席時刻",validators=[DataRequired()])



    def validate_mistime(self,mistime):

        tg_time = self.mistime.data
        sutime = self.sutime.data


        if((tg_time <= sutime)):
            print(tg_time)
            print(sutime)
            raise ValidationError("mistime:erorr")

    
    def validate_notime(self,notime):

        tg_time = self.notime.data
        mistime = self.mistime.data


        if((tg_time <= mistime)):
            print(tg_time)
            print(mistime)
            raise ValidationError("mistime:erorr")
