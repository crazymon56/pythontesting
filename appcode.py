from flask import Flask, request, redirect, url_for, session, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import socket
import codecs
import mysql.connector 
import re
import random
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = "slwol;ayesal."
socketio = SocketIO(app)

UserIn = mysql.connector.connect(user="root", db="chatinformation", passwd="passwordfun", host="mysqldb")



#Chat
@app.route("/BlahChat", methods=['POST', 'GET'])
def chat():
    cursor = UserIn.cursor()
    try:
        if(session['username'] == ''):
            return redirect('Login')
        
        
        
        else:
            # htmltxt = ""
            # cursor.execute("SELECT data FROM userlastdata WHERE useid=(SELECT id FROM users WHERE username=%s)", (session['username'], ))
            # print(cursor.fetchall())
            
            with open('Chat.html', 'r') as fh:        
                html = fh.read()
            return html
    except Exception as e:
        return str(e)


@socketio.on('connectdone', namespace='/test')
def handle_message():
    cursor = UserIn.cursor()
    cursor.execute("SELECT channelid FROM userchannels WHERE useid=(SELECT id FROM users WHERE username=%s);", (session['username'], )) 
    channels = cursor.fetchall()
    if channels:
        for items in channels:
            cursor.execute("SELECT channelname FROM channels WHERE id=%s", (items[0], ))   
            stuff = cursor.fetchone()
            join_room(stuff[0] + '#general')
            if stuff:
                emit('userdata', {'data': stuff[0]})       
    else:
        emit('userdata', {'data': " "})
    emit('username', {'data': session['username']})
    cursor.execute("UPDATE users SET userPMid=%s WHERE username=%s", (request.sid, session['username']))
    UserIn.commit()
    cursor.close()
    

@socketio.on('channelinkget', namespace='/test')
def handel_link(msg):
    cursor = UserIn.cursor()
    cursor.execute("SELECT link FROM channels WHERE channelname=%s", (msg['channel'], ))    
    link = cursor.fetchone()
    emit('sharelinksend', {'data': link[0]})
    cursor.close()

@socketio.on('logout', namespace='/test')
def handle_userdata():
    redirect('Login')

@socketio.on('leave', namespace='/test')
def handle_leave(msg):
    channel = msg['channel']
    chat = msg['chat']
    if chat and channel:
        leave_room(channel + chat)
    else:
        sender = msg['sender']
        reciever = msg['reciever']
        leave_room(sender + reciever + 'PM')


@socketio.on('userspull', namespace='/test')
def handle_users(msg):
    cursor = UserIn.cursor()
    cursor.execute("SELECT username FROM users")
    users = cursor.fetchall()
    for items in users:
        if msg['data'] in str(items):
            emit('userssend', {'user': items})
    cursor.close()

@socketio.on('messagepull', namespace='/test')
def mespull_handle(message):
    cursor = UserIn.cursor()
    if message['PM'] == 'true':
        cursor.execute("SELECT message, datetime FROM PMmessages WHERE senderuserid=(SELECT id FROM users WHERE username=%s) AND recieveruserid=(SELECT id FROM users WHERE username=%s)", (message['sender'], message['reciever']))
        ######WAIT
    else:
        cursor.execute("SELECT message, datetime FROM messages WHERE chatid=(SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s)) AND channelid=(SELECT id FROM channels WHERE channelname=%s)", (message['chat'], message['channel'], message['channel']))
        join_room(message['channel'] + message['chat'])
        messages = cursor.fetchall()
        for items in messages:
            emit('messageload', {'userm': items[0], 'DT': items[1]}, room=message['channel'] + message['chat'])
        emit('messageloaddone')
        cursor.close()

@socketio.on('chatpull', namespace='/test')
def handle_chats(response):
    cursor = UserIn.cursor()
    cursor.execute("SELECT chatid FROM userlastdata WHERE useid=(SELECT id FROM users WHERE username=%s) AND channelid=(SELECT id FROM channels WHERE channelname=%s)", (session['username'], response['channelname']))
    chats = cursor.fetchall()
    for items in chats:
        cursor.execute("SELECT chatname FROM chats WHERE id=%s", (items[0], ))
        stuff = cursor.fetchone()
        join_room(response['channelname'] + stuff[0])
        emit('send', {'data': stuff})
    cursor.close()
    emit('done', {'data': 'true'})

@socketio.on('useresponse', namespace='/test')
def message_handle(message):
    cursor = UserIn.cursor()
    username = session['username']
    if message['PM'] == 'true':
        emit('usermessage', {'userm': message['data'], 'DT': time.asctime(time.localtime()), 'PM': 'true'}, room=message['sender'] + message['reciever'] + 'PM')
        cursor.close()
    else:
        cursor.execute("INSERT INTO messages (datetime, message, userid, chatid, channelid) VALUES(%s, %s, (SELECT id FROM users WHERE username=%s), (SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s)), (SELECT id FROM channels WHERE channelname=%s))", (time.asctime(time.localtime()), message['data'], username, message['chat'], message['channel'], message['channel']))
        emit('usermessage', {'userm': message['data'], 'DT': time.asctime(time.localtime()), 'channel': message['channel'], 'chat': message['chat'], 'PM': 'true', 'reciever': message['reciever']}, room=message['channel'] + message['chat'])
        UserIn.commit()
        cursor.close()

@socketio.on('PMjoin', namespace='/test')
def PMjoining_handle(msg):
    cursor = UserIn.cursor()
    
    if msg['recieve'] == 'true':
        join_room(msg['sender'] + session['username'] + 'PM')
    else:
        join_room(msg['sender'] + msg['reciever'] + 'PM')
        cursor.execute("SELECT userPMid FROM users WHERE username=%s", (msg['reciever'], ))
        PMid = cursor.fetchone()
        emit('PMinfo', {'sending': msg['sender']}, room=PMid[0])
    cursor.close()
    

@socketio.on('userjoin', namespace='/test')
def join_handle_made(sentroom):
    cursor = UserIn.cursor()
    username = session['username']
    check = False
    if sentroom['select'] == 'channel':
        join_room(sentroom['channel'])
        join_room(sentroom['channel'] + '#general')
        text = ""
        possible ="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
        while check == False:    
            for x in range(8):
                num = random.randint(0, 61)
                text = text + possible[num]
            cursor.execute("SELECT link FROM channels WHERE link=%s", (text, ))
            if not cursor.fetchall():    
                cursor.execute("INSERT INTO channels (channelname, link) VALUES(%s, %s)", (sentroom['channel'], text))
                cursor.execute("INSERT INTO chats (chatname, linkid) VALUES('#general', (SELECT id FROM channels WHERE channelname=%s))", (sentroom['channel'], ))
                cursor.execute("INSERT INTO userchannels (useid, channelid) VALUES((SELECT id FROM users WHERE username=%s), (SELECT id FROM channels WHERE channelname=%s))", (username, sentroom['channel']))
                cursor.execute("INSERT INTO userlastdata (useid, channelid, chatid) VALUES((SELECT id FROM users WHERE username=%s), (SELECT id FROM channels WHERE channelname=%s), (SELECT id FROM chats WHERE linkid=(SELECT id FROM channels WHERE channelname=%s)))", (username, sentroom['channel'], sentroom['channel']))
                check = True
                cursor.execute("INSERT INTO messages (message, userid, chatid, channelid) VALUES(%s, (SELECT id FROM users WHERE username=%s), (SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s)), (SELECT id FROM channels WHERE channelname=%s))", (username + ' has joined', username, 'general', sentroom['channel'], sentroom['channel']))

        emit('confirmjoinmessage', {'data' : session['username'] + ' has joined'})
    elif sentroom['select'] == 'join':
        cursor.execute("SELECT channelname FROM channels WHERE link=%s", (sentroom['link'], ))
        if not cursor.fetchall():
            emit('confirmjoin', {'select': 'nochannel'})
        else:
            emit('confirmjoin', {'select': 'channel'})
            cursor.execute("SELECT channelname FROM channels WHERE link=%s", (sentroom['link'], ))
            stuff = cursor.fetchone()
            join_room(stuff[0])
            join_room(stuff[0] + "#general")
            cursor.execute("SELECT id FROM chats WHERE linkid=(SELECT id FROM channels WHERE link=%s)", (sentroom['link'], ))
            chats = cursor.fetchall()
            for items in chats:
                cursor.execute("INSERT INTO userlastdata (useid, channelid, chatid) VALUES((SELECT id FROM users WHERE username=%s), (SELECT id FROM channels WHERE link=%s), %s)", (username, sentroom['link'], items[0]))
                cursor.execute("SELECT chatname FROM chats WHERE id=%s", (items[0], ))
                thechat = cursor.fetchone()
                join_room(stuff[0] + thechat[0])
            cursor.execute("INSERT INTO userchannels (useid, channelid) VALUES((SELECT id FROM users WHERE username=%s), (SELECT id FROM channels WHERE link=%s))", (username, sentroom['link']))
            cursor.execute("SELECT channelname FROM channels WHERE link=%s", (sentroom['link'], ))
            stuff = cursor.fetchone()
            emit('userdata', {'data': stuff[0]})
    else:
        cursor.execute("INSERT INTO chats (chatname, linkid) VALUES(%s, (SELECT id FROM channels WHERE channelname=%s))", (sentroom['chatname'], sentroom['channel']))
        cursor.execute("INSERT INTO userlastdata (useid, channelid, chatid) VALUES((SELECT id FROM users WHERE username=%s), (SELECT id FROM channels WHERE channelname=%s), (SELECT id FROM chats WHERE linkid=(SELECT id FROM channels WHERE channelname=%s) AND chatname=%s))", (username, sentroom['channel'], sentroom['channel'], sentroom['chatname']))
        
        #join_room(sentroom('chatname'))    
    #cursor.execute("INSERT INTO messages (message, userid, chatid, channelid) VALUES(%s, (SELECT id FROM users WHERE username=%s), (SELECT id FROM chats WHERE chatname=%s), (SELECT ))")
    UserIn.commit()
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