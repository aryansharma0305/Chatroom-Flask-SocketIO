from flask import Flask, render_template , request,flash,redirect, session,jsonify,url_for
from flask_socketio import SocketIO ,close_room,join_room,leave_room
import random
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)







app = Flask(__name__,static_url_path='/static')
app.config['SECRET_KEY']='ilovetanu'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///webdatabase.db"
db.init_app(app)
socket=SocketIO(app)

class rooms_db(db.Model):
    
    room: Mapped[str] = mapped_column(primary_key=True)

class players_db(db.Model):
    
    room: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    




with app.app_context():
    db.create_all()




rooms=[]
players={}




def randomroom():
    letters=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    word=''
    while True:
        for i in range(5):
            l=random.choice(letters)
            word+=l
        if word in rooms:
            continue
        else:
            break
    return(word)        





#SOCKETS
#SOCKETS
#SOCKETS


@socket.on("connect")
def handle_connect(obj):
    urlsplit=request.headers.get("Referer").split("?")
    room=urlsplit[0][-5:]
    name=urlsplit[1][12:].replace('+'," ")
    print(room,name)
    sid=request.sid
    try:
        if (sid and room and name and db.get_or_404(rooms_db,room)):
            obj=players_db(room=room,name=name,username=sid)
            db.session.add(obj)
            db.session.commit()
            join_room(room)
            socket.emit('reflectconnect',name,to=room)
            print("```````connected```````")
    except:
        None     


@socket.on('requestplayers')
def handle_players():
    urlsplit=request.headers.get("Referer").split("?")
    room=urlsplit[0][-5:]
    name=urlsplit[1][12:].replace('+'," ")
    data={}

    playerlist=players_db.query.filter_by(room=room).all()
    for i in playerlist:
        data[i.name]=i.username

    socket.emit('player_info',data,to=room)
    None


@socket.on('disconnect')
def handle_disconnect():
    urlsplit=request.headers.get("Referer").split("?")
    room=urlsplit[0][-5:]
    displayname=urlsplit[1][12:].replace('+'," ")
    sid=request.sid
    playerlist=players_db.query.filter_by(room=room).all()
    for i in playerlist:
        if i.name==displayname and i.username==sid:
            db.session.delete(i)
            db.session.commit()
    data={}
    playerlist=players_db.query.filter_by(room=room).all()
    for i in playerlist:
        data[i.name]=i.username

    socket.emit('player_info',data,to=room)
    socket.emit('reflectdisconnect',displayname,to=room)

    try:
        if len(playerlist)==0:
            db.session.delete(db.get_or_404(rooms_db,room))
            db.session.commit()
    except:
        None    




@socket.on('message')
def handle_message(msg):
    urlsplit=request.headers.get("Referer").split("?")
    room=urlsplit[0][-5:]
    name=urlsplit[1][12:].replace('+'," ")
    socket.emit('reflectmessage',{'name':name,'msg':msg},to=room)
    
   
    







# APP ROUTES
# APP ROUTES
# APP ROUTES



@app.route('/',methods=['GET',"POST"])
def chooseroom():
    # return(render_template('chooseroom.html'))
    session.clear
    if request.method=="GET":
        return (render_template('chooseroom.html'))
    
    elif request.method=="POST":
        print(request.form)

        if not( request.form['input_displayname'].strip()):
            print("ERROR")
            return (render_template('chooseroom.html'))

        if 'btn_joinroom' in request.form:
            
            if not(request.form['input_roomid']):
                return (render_template('chooseroom.html'))
            
            
            roomid=request.form['input_roomid']
            name=request.form['input_displayname']
            try:
                if db.get_or_404(rooms_db,roomid):

                    print(roomid,name)
                    return(redirect(url_for('roomlobby',roomID=roomid,displayname=name)))   
            except:
                print("DATABASE EROOR 404") 
                return("INVALID ROOM")  


        elif 'btn_createroom' in request.form:
            roomid=randomroom()
            name=request.form['input_displayname']
            obj=rooms_db(room=roomid)
            db.session.add(obj)
            db.session.commit()
            return(redirect(url_for('roomlobby',roomID=roomid,displayname=name)))

            

        # return(render_template('chooseroom.html'))
        



@app.route('/<roomID>',methods=['GET',"POST"])
def roomlobby(roomID):


    displayname=request.args.get('displayname')

    if not displayname:
        return ('FIRST INITIALIZE')

    try:
        if db.get_or_404(rooms_db,roomID):

            return(render_template('Roomlobby.html',roomID=(roomID.upper()),displayname=displayname   ))
    except:
        print("Database EERROR 404")    
        return ("<h1>INVALID ROOM ID</h1>")




if __name__=="__main__":
    

    app.run(debug=True)
