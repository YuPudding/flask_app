from flask_wtf import FlaskForm
# flask_wtfからFlaskFormをimport
from flask_wtf import FlaskForm
# wtformからフォームに必要なフィールドをimport
from wtforms import StringField, PasswordField, BooleanField, SubmitField,IntegerField,SelectField
# wtformからフォームのバリデーションに必要な機能をimport
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo,NumberRange






class Lesson_Form(FlaskForm):
    lessonname = StringField('授業名',validators=[DataRequired()])
    lessoncount = IntegerField('授業数',validators=[DataRequired(),NumberRange(0, 365)])
    #参加グループ

    join_group = SelectField("参加グループ")
    #担当講師
    join_tuser = SelectField("担当講師")



