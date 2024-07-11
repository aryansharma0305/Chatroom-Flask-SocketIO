from flask import Flask, render_template , request,flash,redirect, session,jsonify,url_for
from flask_socketio import SocketIO ,close_room,join_room,leave_room
import random



app = Flask(__name__,static_url_path='/static')
app.config['SECRET_KEY']='ilovetanu'
socket=SocketIO(app)



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
    if (sid and room and name and room in rooms):
        players[room].append([sid,name])
        join_room(room)
        socket.emit('reflectconnect',name,to=room)
        print("```````connected```````")
    

@socket.on('requestplayers')
def handle_players():
    urlsplit=request.headers.get("Referer").split("?")
    room=urlsplit[0][-5:]
    name=urlsplit[1][12:].replace('+'," ")
    data={}
    for i in players[room]:
        sid=i[0]
        name=i[1]
        data[sid]=name
    socket.emit('player_info',data,to=room)
    None


@socket.on('disconnect')
def handle_disconnect():
    urlsplit=request.headers.get("Referer").split("?")
    room=urlsplit[0][-5:]
    displayname=urlsplit[1][12:].replace('+'," ")

    for i in players[room]:
        sid1=i[0]
        name1=i[1]
        if name1==displayname and sid1==request.sid:
            players[room].remove(i)

    data={}
    for i in players[room]:
        sid=i[0]
        name=i[1]
        data[sid]=name
    socket.emit('player_info',data,to=room)
    
    socket.emit('reflectdisconnect',displayname,to=room)


    try:
        if len(players[room])==0:
            rooms.remove(room)
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

            if roomid in rooms:
                print(roomid,name)
                
                rooms.append(roomid)
                players['roomid']=[]
                
                return(redirect(url_for('roomlobby',roomID=roomid,displayname=name)))
            else:
                return("INVALID ROOM")
            
        elif 'btn_createroom' in request.form:
            roomid=randomroom()
            name=request.form['input_displayname']
            rooms.append(roomid)
            players[roomid]=[]
            return(redirect(url_for('roomlobby',roomID=roomid,displayname=name)))

            

        # return(render_template('chooseroom.html'))
        



@app.route('/<roomID>',methods=['GET',"POST"])
def roomlobby(roomID):

    displayname=request.args.get('displayname')

    if not displayname:
        return ('FIRST INITIALIZE')

    if roomID in rooms:

        return(render_template('Roomlobby.html',roomID=(roomID.upper()),displayname=displayname   ))
    
    else:

        return ("<h1>INVALID ROOM ID</h1>")
    




# if __name__=="__main__":
    

#     app.run(debug=True)
