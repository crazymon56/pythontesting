from flask import Flask, request, redirect, url_for, session, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import socket
import codecs
import mysql.connector 


app = Flask(__name__)
app.config['SECRET_KEY'] = "slwol;ayesal."
socketio = SocketIO(app)

UserIn = mysql.connector.connect(user="root", db="chatinformation", passwd="passwordfun", host="mysqldb")



#Chat
@app.route("/BlahChat", methods=['POST', 'GET'])
def chat():
    try:
        if(session['username'] == ''):
            return 'Please insert a username'
        else:
            with open('Chat.html', 'r') as fh:        
                html = fh.read()
            return html
    except:
        return 'Here Be An Error'


@socketio.on('connected', namespace='/test')
def handle_message():
    cursor = UserIn.cursor()
    try:
        cursor.execute("SELECT data FROM userlastdata WHERE userid=(SELECT id FROM users WHERE username=%s)", (session['username'])) 
        print(cursor)
        cursor.close()
    except:
        pass



@socketio.on('logout', namespace='/test')
def handle_userdata(userdata):
    # cursor = UserIn.cursor()
    # cursor.execute("INSERT INTO data, userid FROM userlastdata VALUES(%s, (SELECT id FROM users WHERE username=%s))", (userdata['data'], session['username']))
    # cursor.close()
    print(userdata['data'])
    redirect('Login')

@socketio.on('useresponse', namespace='/test')
def message_handle(message):
    emit('usermessage', {'data': message['data']})

@socketio.on('userjoin', namespace='/test')
def join_handle(sentroom):
    cursor = UserIn.cursor()
    username = session['username']
    join_room(sentroom['data'])
    # cursor.execute("INSERT INTO chatname FROM chats VALUES(%s)", (sentroom['data']))
    # cursor.execute("INSERT INTO channelname, linkid FROM channels VALUES('general', (SELECT id FROM chats WHERE chatname=%s))", (sentroom['data']))
    # cursor.execute("INSERT INTO message, userid, chatid, channelid FROM messages VALUES(%s, (SELECT id FROM users WHERE username=%s), (SELECT id FROM chats WHERE chatname=%s), (SELECT ))")
    emit('confirmjoin', {'data' : session['username'] + ' has joined'})
    cursor.close()

#SigningUp
@app.route("/SignUpCon", methods=['POST', 'GET'])
def signup():
    cursor = UserIn.cursor()
    if request.form['SPassword'] != request.form['SCPassword']:
        with open('Signup.html', 'r') as fh:        
            html = fh.read()
        return html
    
    cursor.execute("INSERT INTO users (username, password, confirmpassword) VALUES(%s, %s, %s);", (request.form["SUsername"], request.form["SPassword"], request.form["SCPassword"]))
    UserIn.commit()
    cursor.close()

    
    with open('Signupcon.html', 'r') as fh:        
        html = fh.read()
    return html

#Logout
@app.route("/Logout", methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect('Login')        

#Loginpage
@app.route("/Login", methods=['POST', 'GET'])
def login():
    with open('Login.html', 'r') as fh:
        html = fh.read()
        
    return html

#LoginCheck        
@app.route("/Logged", methods=['POST', 'GET'])    
def logged(): 
    cursor = UserIn.cursor()
    if request.method == 'POST':
        session['username'] = request.form['LUsername']
        validlog = 0 
        cursor.execute("SELECT username, password FROM users")
        
        #cursor.execute("label1: LOOP IF users[0] == %s AND users[1] == %s THEN SET %s = %s; ELSE ITERATE label1; END IF; LEAVE label1; END LOOP label1;", (request.form['LUsername'], request.form['LPassword'], validlog, True))
        

        for items in cursor:
            if(items[0] == request.form['LUsername'] and items[1] == request.form['LPassword']):
                validlog = True

        if(validlog == 1):  
            cursor.close()
            return redirect('BlahChat')
                
        else:        
            with open('Invalidlogin.html', 'r') as fh:        
                html = fh.read() 
                cursor.close()       
            return html    
                           

#SignUp
@app.route("/", methods=['GET', 'POST'])
def index():
    cursor = UserIn.cursor()
    cursor.close()
    
    
    with open('Signup.html', 'r') as fh:
        html = fh.read()
        print(html)
        
    return html
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)    