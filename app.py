
from ast import Try
from asyncio import Task
from audioop import add
from cgi import print_environ
from cgitb import text
from collections import UserDict

import math




from sre_constants import IN
from sre_parse import State
from time import struct_time
from tokenize import String, group
from turtle import back
from types import new_class
from urllib import response
from xml.etree.ElementInclude import default_loader

from click import password_option




from flask import Flask, current_app, make_response,session,flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from requests import delete
from sqlalchemy import asc, false, null, true,Table
from sqlalchemy.orm import  relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer,Text,Date,DateTime,Time,Boolean
from sqlalchemy.dialects import postgresql
from flask_migrate import Migrate


import os
from flask import render_template, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user, login_required



from lessontask_form import LessonTask_Form
from lesson_form import Lesson_Form
from room_form import Room_Form
from group_form import Group_Form
from user_form import Tuser_Form, User_Form



from flask_jwt_extended import create_access_token,create_refresh_token,get_jwt_identity, get_jwt
from flask_jwt_extended import current_user as jwt_user
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager


from datetime import datetime, timedelta,date,time




app = Flask(__name__)

#SQLALCHEMY_DATABASE_URI =  "postgres://postgres:postgres@localhost/attend_db" #os.environ.get('DATABASE_URL') #or 

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{password}@{host}/{db_name}?charset=utf8'.format(**{
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'db_name': 'attend_db'
})

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = 'secret-test-test-test'#os.urandom(24)#ランダムだと毎回認証が必要になる


#JWT設定------------------------------------------------------------------------------------


app.config["JWT_SECRET_KEY"] = "sercret-test-test"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)


#jwt初期化
jwt = JWTManager(app)

#-----------------------------------------------------------------------------------

#flask-login初期化

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
	return Tuser.query.get(int(user_id))




# DBとの接続
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#DBテーブル定義


#
ATTEND_NO = 1
ATTEND_SU = 2
ATTEND_MIS = 3


#-------中間テーブル--------------------
class JoinGroups(db.Model):
    __tablename__ = 'joingroups'
    lessonid  = Column(Integer,db.ForeignKey('lesson.lessonid'),primary_key=true)
    groupid = Column(Integer,db.ForeignKey('group.groupid'),primary_key=true)

    delete = Column(Boolean,default=False)

class JoinTusers(db.Model):
    __tablename__ = 'jointusers'
    lessonid = Column(Integer,db.ForeignKey('lesson.lessonid'),primary_key=true)
    tuserid = Column(Integer,db.ForeignKey('tuser.tuserid'),primary_key=true)

    delete = Column(Boolean,default=False)


class TaskLog(db.Model):
    __tablename__ = 'tasklog'
    userid = Column(Integer,db.ForeignKey('user.userid'),primary_key=true)
    lessontaskid = Column(Integer,db.ForeignKey('lessontask.lessontaskid'),primary_key=true)
    atdtime = Column(DateTime)
    state = Column(Integer,db.ForeignKey('atdstate.stateid'))
    delete = Column(Boolean,default=False)

    tasklog_atdstate_re = relationship("AtdState",back_populates="atdstate_tasklog_re")



class AtdState(db.Model):
    __tablename__ = 'atdstate'
    stateid = Column(Integer,primary_key=true)
    statename = Column(Text)

    atdstate_tasklog_re = relationship("TaskLog",back_populates="tasklog_atdstate_re")

#-------------------------------------

#CREATE TABLE
class Tuser(UserMixin,db.Model):
    __tablename__ = 'tuser'
    tuserid = Column(Integer, primary_key=True)
    tusername = Column(Text,unique=true)
    password = Column(Text)

    delete = Column(Boolean,default=False)


    adminid = db.Column(Integer, db.ForeignKey('tuser.tuserid'))
    #リレーションプロパティ
    admin_re = relationship("Tuser",backref='subordinates', remote_side=tuserid)#自己参照




    tuser_group_re = relationship("Group", back_populates="group_tuser_re")#Groupクラス
    tuser_user_re =  relationship("User", back_populates="user_tuser_re")#Userクラス
    tuser_lesson_re =  relationship("Lesson", back_populates="lesson_tuser_re")#Lessonクラス
    tuser_room_re =  relationship("Room", back_populates="room_tuser_re")#Roomクラス



    tuser_lesson_re = relationship("Lesson",back_populates="lesson_tuser_re",secondary=JoinTusers.__tablename__)

    #get_idを入れないと
    #NotImplementedError: No `id` attribute - override `get_id`
    def get_id(self):
        return self.tuserid



#外部キーにnot nullを設定 Tuser以外
#主キーをIntegerで作成


class Group(db.Model):
    __tablename__ = 'group'
    groupid = Column(Integer, primary_key=True)
    groupname = Column(Text)
    adminid = Column(Integer,db.ForeignKey('tuser.tuserid'))

    delete = Column(Boolean,default=False)

    
    group_tuser_re = relationship("Tuser", back_populates="tuser_group_re")#Tuserクラス
    group_user_re = relationship("User",back_populates="user_group_re")

    group_lesson_re = relationship("Lesson",back_populates="lesson_group_re",secondary=JoinGroups.__tablename__)


class User(db.Model):
    __tablename__ = 'user'
    
    userid = Column(Integer, primary_key=false)
    username = Column(Text,unique=true)
    groupid = Column(Integer,db.ForeignKey('group.groupid'))
    password = Column(Text)

    adminid = Column(Integer,db.ForeignKey('tuser.tuserid'))

    delete = Column(Boolean,default=False)

    user_tuser_re =  relationship("Tuser", back_populates="tuser_user_re")#Tuserクラス
    user_group_re = relationship("Group",back_populates="group_user_re")


    user_lessontask_re = relationship("LessonTask",back_populates="lessontask_user_re",secondary=TaskLog.__tablename__)
    user_block_re = relationship("TokenBlocklist",back_populates="block_user_re")


class Lesson(db.Model):
    __tablename__ = 'lesson'


    lessonid = Column(Integer,primary_key=True)
    lessonname = Column(Text)
    lessoncount = Column(Integer)

    adminid = Column(Integer,db.ForeignKey('tuser.tuserid'))

    delete = Column(Boolean,default=False)

    lesson_tuser_re =  relationship("Tuser", back_populates="tuser_lesson_re")#Tuserクラス
    lesson_lessontask_re = relationship("LessonTask",back_populates="lessontask_lesson_re")#LessonTaskクラス

    lesson_tuser_re = relationship("Tuser",back_populates="tuser_lesson_re",secondary=JoinTusers.__tablename__)
    lesson_group_re = relationship("Group",back_populates="group_lesson_re",secondary=JoinGroups.__tablename__)


class Room(db.Model):
    __tablename__ = 'room'

    roomid = Column(Integer,primary_key=True)
    roomname = Column(Text)
    uuid = Column(Text)
    major = Column(Integer)
    minor = Column(Integer)


    adminid = Column(Integer,db.ForeignKey('tuser.tuserid'))
    delete = Column(Boolean,default=False)

    room_tuser_re =  relationship("Tuser", back_populates="tuser_room_re")#Tuserクラス
    room_lessontask_re = relationship("LessonTask",back_populates="lessontask_room_re")#LessonTaskクラス


class LessonTask(db.Model):
    __tablename__ = 'lessontask'

    lessontaskid =  Column(Integer,primary_key=True)
    lessontaskdate =  Column(Date)
    periode = Column(Integer)

    lessonid = Column(Integer,db.ForeignKey('lesson.lessonid'))
    roomid = Column(Integer,db.ForeignKey('room.roomid'))

    sutime = Column(Time)
    mistime = Column(Time)
    notime = Column(Time)

    delete = Column(Boolean,default=False)

    lessontask_lesson_re = relationship("Lesson",back_populates="lesson_lessontask_re")
    lessontask_room_re = relationship("Room",back_populates="room_lessontask_re")


    lessontask_user_re = relationship("User",back_populates="user_lessontask_re",secondary=TaskLog.__tablename__)

    def toDict(self):
        model = {}
        for column in self.__table__.columns:
            model[column.name] = str(getattr(self, column.name))
        return model


#----------------------スマホアプリAPI----------------------------


class TokenBlocklist(db.Model):
    id = Column(Integer, primary_key=True)
    jti = Column(Text, nullable=False, index=True)
    created_at = Column(DateTime,default=datetime.now(),nullable=False)
    userid = Column(Integer,db.ForeignKey('user.userid'),
                default=lambda:jwt_user.userid)
    delete_flg = Column(Boolean,default=True)

    block_user_re = relationship("User",back_populates="user_block_re")





#---------------jwtコールバック------------------------------------------


# create_access_token(..)実行時に起動する。
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.userid


# @jwt_requiredが付与されている関数の実行前に起動する。
# (つまりリソースにアクセスした時)
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(userid=identity).one_or_none()


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    print("blocklist")
    return token is not None

#------------------------------------------------------------------------


#OK
@app.route("/api_login", methods=["POST"])
def au_in():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(username=username).one_or_none()

    #POSTされたパスワードとユーザ名が正しいかどうか
    if not user or not check_password_hash(user.password, password): 
        return jsonify({"msg":"Wrong username or password"}), 401


    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)


    return jsonify(access_token=access_token, refresh_token=refresh_token),200

#OK
@app.route("/api_refresh", methods=["POST"])
@jwt_required(refresh=True)
def api_refresh():
    user_identity = get_jwt_identity() #ユーザ情報の取得????

    user = User.query.filter_by(userid=user_identity).first()
    access_token = create_access_token(identity=user)
    return jsonify(access_token=access_token),200

#OK
@app.route("/api_logout", methods=["DELETE"])
@jwt_required(verify_type=False)
def modify_token():
    token = get_jwt()
    jti = token["jti"]
    ttype = token["type"]
    now = datetime.now()


    new_block = TokenBlocklist()
    new_block.jti  = jti
    new_block.created_at = now

    db.session.add(new_block)
    db.session.commit()
    return jsonify(msg=f"{ttype.capitalize()} token successfully revoked"),200


#念のためAPIはtry exceptを実装する
#OK
@app.route("/api_protected", methods=["POST"])
@jwt_required(verify_type=False)
def api_protected():
    return jsonify(get_jwt()),200



#READY
@app.route("/api_gettask",methods=["POST"])#割り当てられたタスクの取得
@jwt_required()
def get_task():
    #ユーザ情報の取得

    # １今日の日付のTaskを取得 delete=false
    # ２そのうちのroomを結合 delete=false
    # ３ ユーザIDがuseridかつstate=0 かつ　delete=false のtasklogを抽出して
    # ４　tasklog と　task　lessonを結合

    #今日のひづけを取得
    today = date.today().strftime('%Y-%m-%d')

    userid = get_jwt_identity()

    result = db.session.execute("WITH get_taskid as ( "+
                                "SELECT * FROM lessontask l "+
                                "JOIN room r on l.roomid = r.roomid "+
                                "WHERE l.delete = false and r.delete = false "+
                                " and l.lessontaskdate = :todate ) " + 
                                        #授業名,部屋名、ビーコン番号,(タスク実行日),開始時間,遅刻時間,終了時間
                                "SELECT l.lessonname,gt.roomname,gt.uuid,gt.major,gt.minor,gt.lessontaskdate,gt.periode,gt.sutime,gt.mistime,gt.notime " +
                                "FROM Tasklog tl "+
                                "JOIN get_taskid gt ON tl.lessontaskid = gt.lessontaskid "+
                                "JOIN lesson l ON gt.lessonid = l.lessonid "+
                                "WHERE tl.userid = :userid and tl.delete = false and l.delete = false and tl.state = 0 "
                                ,{"todate":today,'userid':userid})
    

    data = {}
    #返す値のキー
    key = ["lessonname","roomname","uuid","major","minor","date","periode","sutime","mistime","notime"]
    for i,row in enumerate(result):
        res = {}
        for index,col in enumerate(row):
            if(type(col) == date):
                col = col.strftime('%Y-%m-%d')
            if(type(col) == time):
                col = col.strftime('%H:%M:%S')
            res[key[index]] = col
        data[i] = res


    #jsonとして返す
    
    return jsonify(data),200

#READY
@app.route("/api_attend",methods=["POST"])#タスクに対する出席処理
@jwt_required()
def attend():
#taskid 
#userid
#stateをポストして
#データの更新を行う

    try:

        taskid = request.json.get("taskid", None)
        userid = get_jwt_identity()
        state = request.json.get("state", None)
        atd_time = time.now()#request.json.get("taskid", None)

        tasklog = TaskLog.query.filter_by(lessontaskid=taskid,userid=userid).first()

        if(tasklog is not None):
            tasklog.state = state
            db.session.commit()
            return jsonify({'msg':'tasklog update'}),200
        return jsonify({"msg":"tasklog none"}),401
    except Exception as e:
        return jsonify({'msg':'upate faild'}),401




#READY
@app.route("/api_get_lesson",methods=["POST"])#参加中のレッスン
@jwt_required()
def get_joinlesson():

    # 1 jwtのユーザIDからGroupID
    # 2 JoinGroupからLessonIDを取得
    # 3 LessonのID,LessonのNameを返す

    try:
        userid = get_jwt_identity()#jwt
        user = User.query.filter_by(userid=userid).first()
    except:
        return {"msg","db_error1"}

    if (user is not None):

        try:
            groupid = user.groupid
            result =  db.session.execute(
                    "SELECT l.lessonid,l.lessonname FROM joingroups jg "
                    +"JOIN lesson l ON l.lessonid = jg.lessonid "
                    +"WHERE jg.groupid = :groupid ",{"groupid":groupid}
                    )
                
            data = {}
                #返す値のキー
            key = ["lessonid","lessonname"]
            for i,row in enumerate(result):
                    res = {}
                    for index,col in enumerate(row):
                        if(type(col) == date):
                            col = col.strftime('%Y-%m-%d')
                        if(type(col) == time):
                            col = col.strftime('%H:%M:%S')
                        res[key[index]] = col
                    data[i] = res
            return jsonify(data),200
        except:
            return jsonify({"msg":"db_error2"}),401

    return jsonify({"msg":"user none"}),401

#NO
#出席必要日数が不足
@app.route("/api_get_lesson_detail",methods=["POST"])#ユーザの出席率、ログの取得
@jwt_required()
def get_lesson_detail():


    #一つの授業に対するユーザ一人の集計情報を取得
    #授業ID
    #ユーザID


    #TaskLogに対しての集計を行う
    #出席率　state=1の行数/Count(*)
    #欠席率  state=0行数/Count(*)
    #遅刻率　state=2の行数/COunt(*
    #)

    #lessonidの指定
    #ユーザidの指定
    lessonid = request.json.get("lessonid", None);

    userid = get_jwt_identity()

    print(lessonid)
    print(userid)

    task_count = 0 #全体のtask数を数える
    alltask = 0 #予定授業数を入れる
    


    at_count = {} #順番に項目を加えてい行く
    at_per = {}
    key = ["no","su","mis"]


    
    #ここに出席状況別のデータ一覧を入れる(初期は20件くらい???)
    data_list = {}#Sqlalchemyのオブジェクトは通常jsonかできないので再度辞書化


    try:
        result = db.session.execute("WITH get_taskid as(SELECT * FROM  lessontask l " + 
                        "WHERE l.lessonid = :lessonid) " +

                        ", get_task as(SELECT * FROM tasklog tl " +
                        "JOIN get_taskid gt ON gt.lessontaskid = tl.lessontaskid " +
                        "WHERE tl.userid = :userid) "+

                        "SELECT a.stateid,COUNT(gt.state) FROM get_task gt " +
                        "RIGHT OUTER JOIN atdstate a ON a.stateid = gt.state " +
                        "GROUP BY a.stateid "+
                        "ORDER BY a.stateid ASC",{"lessonid":lessonid,"userid":userid})

        lesson= Lesson.query.filter_by(lessonid=lessonid).first()
        alltask = lesson.lessoncount

        for index,row in enumerate(result):
            print("index")
            #row[0]でstaetidを取得それを用いて
            #su_list などをを取得

            #辞書化して入れる
            
            list = []

            #最初の20件を取得
            for tl in TaskLog.query.filter_by(userid=userid,state=row[0]).offset(0).limit(20):
                list.append(LessonTask.query.filter_by(lessontaskid=tl.lessontaskid,lessonid=lessonid).first().toDict())



            data_list[key[index]] = list

            print("a")

            if(type(row[1]) == int):
                task_count = task_count + int(row[1])
                at_count[key[index]] = int(row[1])

    
        for key in at_count.keys():

            per = at_count[key]/task_count * 100
            if(key == "mis"):
                at_per[key] = math.ceil(per*10)/10 #遅刻のみ切り上げで計算
            else:
                at_per[key] = math.floor(per*10)/10
    except Exception as e:
        print(e)
        return jsonify({"msg":"db_error"}),401

    # print(data_list)
    # print(alltask)
    # print(task_count)
    # print(at_count)
    #print(at_per)

    return jsonify({"nowtask-num":task_count,"atd_per":at_per,"datalist":data_list}),200


#ready
@app.route("/api_get_log_update",methods=["POST"])#出席、遅刻、欠席の各ログの更新 
@jwt_required()
def get_log_update():

    lessonid = request.json.get("lessonid", None)
    userid =  get_jwt_identity()
    offset_x = request.json.get("offset", None) #post
    state = request.json.get("state", None) #post


    list =[]
    limit_num = 20 #取得する個数
    offset_num = limit_num*offset_x# offsetx:0 0~20  offsetx:1 21~40
    

    #クエリ確認方法
    # print(query.statement.compile(
    #         dialect=mysql.dialect(),
    #         compile_kwargs={"literal_binds": True}))

    try:
        query = TaskLog.query.filter_by(userid=userid,state=state).offset(offset_num).limit(limit_num)
        for tl in query:
            list.append(LessonTask.query.filter_by(lessontaskid=tl.lessontaskid,lessonid=lessonid).first().toDict())
        return jsonify({"data":list})
    except:
        return jsonify({"msg","db_error"})

#----------------------Web管理側API--------------------------------
def getNextval(sequencename):

    result = db.session.execute("SHOW TABLE STATUS LIKE :table_name",{"table_name":sequencename})
    for row in result:
        userDict = dict(row)
        nextval = int(userDict['Auto_increment'])
    return nextval

def TestDataADD():
    Tuser1 = Tuser()
    Tuser1.tusername = 'T1'
    Tuser1.password = 'T1'
    db.session.add(Tuser1)
    db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@login_required
def main():

    print(current_user.tuserid)

    #データがない場合はどうなる??
    lessons = Lesson.query.filter_by(adminid=current_user.tuserid).order_by(asc(Lesson.lessonid))
    return render_template('index.html',current_user=current_user,lessons=lessons)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    #ログイン済みの場合
    if current_user.is_authenticated:
        return redirect('/')

    if request.method == "POST":


        #実際はバリデーションをかける
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            new_tuser = Tuser()
            new_tuser.tusername = username
            new_tuser.password = password=generate_password_hash(password, method='sha256')
            db.session.add(new_tuser)
            db.session.commit()
            return redirect('/')
        except  Exception as e :
            #ユーザが重複していた場合のエラーをだす
            flash(e)
            flash('ユーザ作成失敗')
            return render_template('signup.html')
    else:

        
        return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    #ログイン済みの場合
    if current_user.is_authenticated:
        return redirect('/')

    if request.method == "POST": 

        username = request.form.get('username')
        password = request.form.get('password')
        tuser = Tuser.query.filter_by(tusername=username).first()

        if tuser is None or not check_password_hash(tuser.password, password):
            # usernameまたはpasswordが誤っている旨のflashを表示
            flash('ユーザ名またはパスワードが間違っている')
            return redirect('/login')
        else:
            login_user(tuser)
            return redirect('/')

    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/lesson_ad', methods=['GET', 'POST'])
@login_required
def lesson_ad():
    form =  Lesson_Form()

    form.join_group.choices = [(g.groupid, g.groupname) for g in Group.query.filter_by(adminid=current_user.tuserid).order_by('groupid')]
    form.join_tuser.choices = [(g.tuserid, g.tusername) for g in Tuser.query.filter_by(adminid=current_user.tuserid).order_by('tuserid')]

    if request.method == "POST": 


        #form.validate_on_submit() #何も設定されていない場合はFalse?

        try:

        
            nextval = getNextval('lesson')



            name = form.lessonname.data
            count = form.lessoncount.data

            new_lesson = Lesson()
            new_lesson.lessonid = nextval
            new_lesson.lessonname = name
            new_lesson.lessoncount = count
            new_lesson.adminid = current_user.tuserid                      
            new_joingroups = JoinGroups()
            new_joingroups.groupid = form.join_group.data
            new_joingroups.lessonid = nextval


            new_jointusers = JoinTusers()
            new_jointusers.lessonid = nextval
            new_jointusers.tuserid = form.join_tuser.data



            db.session.add(new_lesson)
            db.session.commit()

            db.session.add(new_joingroups)
            db.session.add(new_jointusers)

            db.session.commit()

            return redirect('/')
        except Exception as e:#例外が発生しても流れてくれない????
            flash(e)
            flash('授業データ作成失敗')
            return redirect('/lesson_ad')
    else:
        return render_template('lesson_ad_ed.html',form=form)

@app.route('/lesson_ed/<int:id>', methods=['GET', 'POST'])
@login_required
def lesson_ed(id):
    form =  Lesson_Form()
    form.join_group.choices = [(g.groupid, g.groupname) for g in Group.query.filter_by(adminid=current_user.tuserid).order_by('groupid')]
    form.join_tuser.choices = [(g.tuserid, g.tusername) for g in Tuser.query.filter_by(adminid=current_user.tuserid).order_by('tuserid')]
    lesson = Lesson.query.get(id)

    if request.method == "POST": 
        
        #データ変更処理

        name = form.lessonname.data
        count = form.lessoncount.data

        lesson.lessonname = name
        lesson.lessoncount = count 
        db.session.commit()


        #JoinUser
        #JoinGroupの設定変更


        return redirect('/')
    else:
        form.lessonname.data = lesson.lessonname
        form.lessoncount.data = lesson.lessoncount
        return render_template('lesson_ad_ed.html',form=form,mode="edit")

@app.route('/lesson_de/<int:id>', methods=['GET', 'POST'])
@login_required
def lesson_detail(id):
    lesson = Lesson.query.get(id)
    lessontask =  LessonTask.query.filter_by(lessonid=id).order_by(asc(LessonTask.lessontaskid))
    return render_template('lesson_de.html',lesson=lesson,lessontasks = lessontask)

@app.route('/lessontask_de/<int:id>', methods=['GET', 'POST'])
@login_required
def lessontask_de(id):
    tasklog = TaskLog.query.filter_by(lessontaskid=id).all()
    #user情報と結合
    return render_template('lessontask_de.html',tasklogs=tasklog)

@app.route('/room_ad',methods=['GET', 'POST'])
@login_required
def room_add():
    form = Room_Form()
    if request.method == "POST":

        try:
            new_room = Room()
            new_room.roomname = form.roomname.data
            new_room.uuid = form.uuid.data
            new_room.major = form.major.data
            new_room.minor = form.minor.data
            new_room.adminid = current_user.tuserid

            db.session.add(new_room)
            db.session.commit()
            return redirect('/')
        except:
            return print('ERROR')

    else:
        return render_template('room_ad_ed.html',form=form)

@app.route('/group_ad',methods=['GET', 'POST'])
@login_required
def group_add():
    form = Group_Form()
    if request.method == "POST":

        try:
            new_group = Group()

            new_group.groupname = form.groupname.data
            new_group.adminid = current_user.tuserid

            db.session.add(new_group)
            db.session.commit()
            return redirect('/userlist')
        except:
            return 'error'
    else:
        return render_template('group_ad_ed.html',form=form)

@app.route('/user_ad',methods=['GET', 'POST'])
@login_required
def user_add():
    form = User_Form()
    groups = []
    groups.append((0,'未設定'))
    for  g in Group.query.order_by('groupid'):
        groups.append((g.groupid, g.groupname))
    form.groupid.choices = groups

    if request.method == "POST":


        try:
            new_user = User()
            new_user.username = form.username.data
            
            if(form.groupid.data != "0"): #dataは文字列型で飛んでくる
                new_user.groupid = form.groupid.data

            new_user.password = generate_password_hash(form.password.data, method='sha256')
            new_user.adminid = current_user.tuserid
            db.session.add(new_user)
            db.session.commit()
            return redirect('/userlist')
        except:
            flash('ユーザ作成失敗')
            return redirect('user_ad')
    else:
        return render_template('user_ad_ed.html',form=form)

@app.route('/tuser_ad',methods=['GET', 'POST'])
@login_required
def tuser_add():
    form = Tuser_Form()
    if request.method == "POST":
        try:
            new_tuser = Tuser()
            new_tuser.tusername = form.tusername.data
            new_tuser.password = generate_password_hash(form.password.data, method='sha256')
            new_tuser.adminid = current_user.tuserid
            
            db.session.add(new_tuser)
            db.session.commit()
            return redirect('/userlist')
        except:
            flash('ユーザ作成失敗')
            return redirect('tuser_ad')
    else:
        return render_template('tuser_ad_ed.html',form=form)

@app.route('/userlist',methods=['GET', 'POST'])
@login_required
def userlist():
    users = User.query.filter_by(adminid=current_user.tuserid).order_by('userid').all()
    tusers = Tuser.query.filter_by(adminid=current_user.tuserid).order_by('tuserid').all()
    return render_template('userlist.html',users=users,tusers=tusers)

@app.route('/lessontask_ad/<int:id>',methods=['GET', 'POST'])
@login_required
def lessontask_add(id):

    # validate_on_submit() が choices に対してバリデーションを行なっているため、 
    # validate_on_submit() より後に choices を追加するとエラーになってしまう

    form = LessonTask_Form()
    rooms = []
    for r in Room.query.order_by('roomid'):
            rooms.append((r.roomid, r.roomname))
    form.roomid.choices = rooms


    if request.method == "POST":
        try:
            if form.validate_on_submit():

                nextval = getNextval('lessontask')
                new_lessontask = LessonTask()
                new_lessontask.lessontaskid = nextval
                new_lessontask.lessontaskdate = form.lessontaskdate.data
                new_lessontask.periode = form.periode.data
                new_lessontask.lessonid = id
                new_lessontask.roomid = form.roomid.data
                new_lessontask.sutime = form.sutime.data
                new_lessontask.mistime = form.mistime.data
                new_lessontask.notime = form.notime.data

                db.session.add(new_lessontask)
                db.session.commit() 

                add_datas =  []
                #TaskLog表への追加
                for g in JoinGroups.query.filter_by(lessonid=id).order_by('groupid'):
                    for u in User.query.filter_by(groupid=g.groupid).order_by('userid'):
                        new_task_log = TaskLog()
                        new_task_log.userid = u.userid
                        new_task_log.lessontaskid = new_lessontask.lessontaskid
                        new_task_log.state = ATTEND_NO
                        add_datas.append(new_task_log)
                print(add_datas)

                
                

                db.session.add_all(add_datas)
                db.session.commit()

                #flushで一時的に保存
                #トランザクション毎にtry catchを取得とかにするべき
                #commit
                return redirect('/lesson_de/' + str(id))
                
            else:
                flash('バリデーションNO')
                return render_template('lessontask_ad_ed.html',form=form)
                #redirect を行うとform要素がリセットされる
        except Exception as e:
            print(e)
            flash("タスク作成失敗")
            return redirect('/lessontask_ad/' + str(id))
    else:        
        return render_template('lessontask_ad_ed.html',form=form)


#部屋編集機能
# @app.route('/room_ed/<int:id>')
# @login_required
# def room_edit(id):

def add_state():


    no = AtdState()
    no.stateid = ATTEND_NO
    no.statename = 'no'
    su = AtdState()
    su.stateid = ATTEND_SU
    su.statename = 'su'
    mis = AtdState()
    mis.stateid = ATTEND_MIS
    mis.statename = 'mis' 

    ad = [no,su,mis]
    db.session.add_all(ad)
    db.session.commit()

def atd_detail_test():

                lesson_id = 1

                nextval = getNextval('lessontask')
                new_lessontask = LessonTask()
                new_lessontask.lessontaskid = nextval
                # new_lessontask.lessontaskdate = form.lessontaskdate.data
                # new_lessontask.periode = form.periode.data
                new_lessontask.lessonid = lesson_id
                # new_lessontask.roomid = form.roomid.data
                # new_lessontask.sutime = form.sutime.data
                # new_lessontask.mistime = form.mistime.data
                # new_lessontask.notime = form.notime.data

                db.session.add(new_lessontask)
                db.session.commit() 

                #TaskLog表への追加

                new_task_log = TaskLog()
                new_task_log.userid = 1
                new_task_log.lessontaskid = new_lessontask.lessontaskid
                new_task_log.state = ATTEND_SU
                new_task_log.atdtime = datetime.now()

                db.session.add(new_task_log)
                db.session.commit()


if __name__ == '__main__':
    #atd_detail_test()
    #add_state()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)