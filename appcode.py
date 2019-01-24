from flask import Flask, request, redirect, url_for, session, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import socket
import codecs
import mysql.connector 
import re
import random
import time
import shutil

UPLOAD_FOLDER = "/home/cthigpen/dockerstuff/Messingaround/gittest/pythontesting/usersimages"
ALLOWED_EXTENSIONS = set(['txt'])

app = Flask(__name__)
app.config['SECRET_KEY'] = "slwol;ayesal."
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO(app)

UserIn = mysql.connector.connect(user="root", db="chatinformation", passwd="passwordfun", host="mysqldb")



#Chat
@app.route("/BlahChat", methods=['POST', 'GET'])
def chat():
    cursor = UserIn.cursor()
    try:
        if session['username']:
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
    username = session['username']
    cursor.execute("SELECT channelid FROM userchannels WHERE useid=(SELECT id FROM users WHERE username=%s);", (session['username'], )) 
    channels = cursor.fetchall()
    if channels:
        for items in channels:
            cursor.execute("SELECT channelname FROM channels WHERE id=%s", (items[0], ))   
            stuff = cursor.fetchone()
            join_room(stuff[0])
            cursor.execute("SELECT id FROM users WHERE username=%s", (username, ))
            userid = cursor.fetchone()
            cursor.execute("SELECT ownerid FROM channels WHERE channelname=%s", (str(stuff[0]), ))
            ownerid = cursor.fetchone()
            if stuff:
                if userid == ownerid:
                    emit('userdata', {'data': stuff[0], 'sentdata': 'channel', 'owner': 'true'})                           
                else:
                    emit('userdata', {'data': stuff[0], 'sentdata': 'channel', 'owner': 'false'})       
    else:
        emit('userdata', {'data': " ", 'sentdata': 'channel'})
    cursor.execute("SELECT openedPM FROM PMopen WHERE userid=(SELECT id FROM users WHERE username=%s)", (username, ))
    PMS = cursor.fetchall()
    if PMS:
        for items in PMS:
            cursor.execute("SELECT username FROM users WHERE id=%s", (items[0], ))
            stuff = cursor.fetchone()
            emit('userdata', {'data': stuff[0], 'sentdata': 'PM'})
    emit('userdata', {'data': " ", 'sentdata': 'PM'})
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
    cursor = UserIn.cursor()
    username = session['username']
    cursor.execute("SELECT channelid FROM userchannels WHERE useid=(SELECT id FROM users WHERE username=%s)", (username, ))
    channels = cursor.fetchall()
    for items in channels:
        cursor.execute("SELECT channelname FROM channels WHERE id=%s", (items[0], ))
        channelname = cursor.fetchone()
        leave_room(channelname[0])

@socketio.on('userspull', namespace='/test')
def handle_users(msg):
    cursor = UserIn.cursor()
    username = session['username']
    cursor.execute("SELECT username FROM users")
    users = cursor.fetchall()
    for items in users:
        if msg['data'] in str(items):
            if items[0] != username: 
                emit('userssend', {'user': items})
    cursor.close()

@socketio.on('messagepull', namespace='/test')
def mespull_handle(message):
    cursor = UserIn.cursor()
    username = session['username']
    if message['PM'] == 'true':
        temp = [-1]
        cursor.execute("SELECT lastmesid FROM PMopen WHERE userid=(SELECT id FROM users WHERE username=%s) AND openedPM=(SELECT id FROM users WHERE username=%s)", (username, message['reciever']))
        result = cursor.fetchone()
        if result[0] != 0:
            temp = result
            cursor.execute("UPDATE PMopen SET lastmesid=0 WHERE userid=(SELECT id FROM users WHERE username=%s) AND openedPM=(SELECT id FROM users WHERE username=%s)", (username, message['reciever']))
        if message['extraload']:
            numberofmessages = (message['num'] + 1) * 45
            cursor.execute("SELECT message, datetime, id FROM PMmessages WHERE (senderuserid=(SELECT id FROM users WHERE username=%s) OR senderuserid=(SELECT id FROM users WHERE username=%s)) AND (recieveruserid=(SELECT id FROM users WHERE username=%s) OR recieveruserid=(SELECT id FROM users WHERE username=%s)) ORDER BY id DESC LIMIT %s", (message['sender'], message['reciever'], message['sender'], message['reciever'], numberofmessages))
            messages = cursor.fetchall()
            del messages[0:message['num'] * 45]
        else:
            cursor.execute("SELECT message, datetime, id FROM PMmessages WHERE (senderuserid=(SELECT id FROM users WHERE username=%s) OR senderuserid=(SELECT id FROM users WHERE username=%s)) AND (recieveruserid=(SELECT id FROM users WHERE username=%s) OR recieveruserid=(SELECT id FROM users WHERE username=%s)) ORDER BY id DESC LIMIT 45", (message['sender'], message['reciever'], message['sender'], message['reciever']))
            messages = cursor.fetchall()
        for items in messages:
            if items[2] == temp[0]:
                emit('messageload', {'userm': items[0], 'DT': items[1], 'newmesstart': 'true'})
            else:
                emit('messageload', {'userm': items[0], 'DT': items[1], 'newmesstart': 'false'})
        emit('messageloaddone')
    else:
        # cursor.execute("SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s)", (message['chat'], message['channel']))
        # chats = cursor.fetchone
        # if not channels:
        #     emit('messageload', {'userm': "This channel has been deleted", 'DT': "", 'newmesstart': 'false'})   
        # else:
        #     if not chats:
        #         emit('messageload', {'userm': "This chat has been deleted", 'DT': "", 'newmesstart': 'false'})
        #     else:
        temp = [-1]
        cursor.execute("SELECT lastmesid FROM userlastdata WHERE useid=(SELECT id FROM users WHERE username=%s) AND channelid=(SELECT id FROM channels WHERE channelname=%s) AND chatid=(SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s))", (username, message['channel'], message['chat'], message['channel']))
        result = cursor.fetchone()
        if result[0] != 0:
            temp = result
            cursor.execute("UPDATE userlastdata SET lastmesid=0 WHERE useid=(SELECT id FROM users WHERE username=%s) AND channelid=(SELECT id FROM channels WHERE channelname=%s) AND chatid=(SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s))", (username, message['channel'], message['chat'], message['channel']))
        if message['extraload']:
            numberofmessages = (message['num'] + 1) * 45
            cursor.execute("SELECT message, datetime, id, imagemes FROM messages WHERE chatid=(SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s)) AND channelid=(SELECT id FROM channels WHERE channelname=%s) ORDER BY id DESC LIMIT %s", (message['chat'], message['channel'], message['channel'], numberofmessages))
            messages = cursor.fetchall()
            del messages[0:message['num'] * 45]
        else:
            cursor.execute("SELECT message, datetime, id, imagemes FROM messages WHERE chatid=(SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s)) AND channelid=(SELECT id FROM channels WHERE channelname=%s) ORDER BY id DESC LIMIT 45", (message['chat'], message['channel'], message['channel']))
            messages = cursor.fetchall()
        for items in messages:
            base64 = ""
            if items[2] == temp[0]:
                if items[3] == 'yes':
                    cursor.execute("SELECT id FROM channels WHERE channelname=%s", (message['channel'], ))
                    channel = cursor.fetchone()
                    cursor.execute("SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s)", (message['chat'], message['channel']))
                    chat = cursor.fetchone()
                    cursor.execute("SELECT userid FROM messages WHERE id=%s", (items[2], ))
                    user = cursor.fetchone()
                    messageid = items[2]
                    num = 1000
                    find = False
                    while find == False:
                        if channel[0] > num:
                            num = num + 1000
                        else:
                            find = True                    
                    path = "usersimages/" + str(num) + "/" + str(channel[0]) + "/" + str(chat[0])
                    filename = str(user[0]) + "," + str(messageid[0])
                    with open(os.path.join(path, filename), "r") as fh:
                       base64 = fh.read()
                emit('messageload', {'userm': items[0], 'image': base64, 'DT': items[1], 'newmesstart': 'true'})   
            else:
                if items[3] == 'yes':
                    cursor.execute("SELECT id FROM channels WHERE channelname=%s", (message['channel'], ))
                    channel = cursor.fetchone()
                    cursor.execute("SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s)", (message['chat'], message['channel']))
                    chat = cursor.fetchone()
                    cursor.execute("SELECT userid FROM messages WHERE id=%s", (items[2], ))
                    user = cursor.fetchone()
                    messageid = items[2]
                    num = 1000
                    find = False
                    while find == False:
                        if channel[0] > num:
                            num = num + 1000
                        else:
                            find = True                    
                    path = "usersimages/" + str(num) + "/" + str(channel[0]) + "/" + str(chat[0])
                    filename = str(user[0]) + "," + str(messageid)
                    with open(os.path.join(path, filename), "r") as fh:
                        base64 = fh.read()
                emit('messageload', {'userm': items[0], 'image': base64, 'DT': items[1], 'newmesstart': 'false'})
        emit('messageloaddone')
        UserIn.commit()
        cursor.close()


@socketio.on('chatpull', namespace='/test')
def handle_chats(response):
    cursor = UserIn.cursor()
    username = session['username']
    cursor.execute("SELECT chatid FROM userlastdata WHERE useid=(SELECT id FROM users WHERE username=%s) AND channelid=(SELECT id FROM channels WHERE channelname=%s)", (username, response['channelname']))
    chats = cursor.fetchall()
    for items in chats:
        cursor.execute("SELECT chatname FROM chats WHERE id=%s", (items[0], ))
        stuff = cursor.fetchone()
        cursor.execute("SELECT lastmesid FROM userlastdata WHERE useid=(SELECT id FROM users WHERE username=%s) AND channelid=(SELECT id FROM channels WHERE channelname=%s) AND chatid=(SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s))", (username, response['channelname'], stuff[0], response['channelname']))
        lastmesid = cursor.fetchone()
        if lastmesid[0] != 0:
            emit('send', {'data': stuff, 'notify': 'true'})
        else:
            emit('send', {'data': stuff[0], 'notify': 'false'}, namespace='/test')   
    cursor.close()
    emit('done', {'data': 'true'}, namespace='/test')

@socketio.on('useresponse', namespace='/test')
def message_handle(message):
    cursor = UserIn.cursor()
    username = session['username']
    if message['PM'] == 'true':
        Mestime = time.asctime(time.localtime())
        if message['data']:
            cursor.execute("SELECT userPMid FROM users WHERE username=%s", (message['reciever'], ))
            recieverid = cursor.fetchone()
            cursor.execute("INSERT INTO PMmessages (datetime, message, senderuserid, recieveruserid) VALUES(%s, %s, (SELECT id FROM users WHERE username=%s), (SELECT id FROM users WHERE username=%s))", (Mestime, message['data'], message['sender'], message['reciever']))
            emit('usermessage', {'userm': message['data'], 'DT': Mestime, 'PM': 'true', 'sender': "_", 'reciever': message['reciever']})
            emit('usermessage', {'userm': message['data'], 'DT': Mestime, 'PM': 'true', 'sender': message['sender'], 'reciever': "_"}, room=recieverid[0])
        else:
            cursor.execute("SELECT id FROM PMopen WHERE userid=(SELECT id FROM users WHERE username=%s) AND openedPM=(SELECT id FROM users WHERE username=%s)", (username, message['sender']))
            check = cursor.fetchone()
            if not check:
                cursor.execute("INSERT INTO PMopen (userid, openedPM, lastmesid) VALUES((SELECT id FROM users WHERE username=%s), (SELECT id FROM users WHERE username=%s), 0)", (username, message['sender']))
            cursor.execute("SELECT lastmesid FROM PMopen WHERE userid=(SELECT id FROM users WHERE username=%s) AND openedPM=(SELECT id FROM users WHERE username=%s)", (username, message['sender']))
            result = cursor.fetchone()
            if result[0] == 0:
                cursor.execute("SELECT id FROM PMmessages WHERE senderuserid=(SELECT id FROM users WHERE username=%s) AND recieveruserid=(SELECT id FROM users WHERE username=%s) AND datetime=%s", (message['sender'], username, message['DT']))
                result = cursor.fetchone()
                cursor.execute("UPDATE PMopen SET lastmesid=%s WHERE userid=(SELECT id FROM users WHERE username=%s) AND openedPM=(SELECT id FROM users WHERE username=%s)", (result[0], username, message['sender']))    
    else:
        Mestime = time.asctime(time.localtime())
        if message['data']:
            if message['Ifile']:
                cursor.execute("INSERT INTO messages (datetime, imagemes, message, userid, chatid, channelid) VALUES(%s, %s, %s, (SELECT id FROM users WHERE username=%s), (SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s)), (SELECT id FROM channels WHERE channelname=%s))", (Mestime, 'yes',  message['data'], username, message['DOWNchat'], message['DOWNchannel'], message['DOWNchannel']))
                UserIn.commit()
                
                cursor.execute("SELECT id FROM channels WHERE channelname=%s", (message['DOWNchannel'], ))
                channel = cursor.fetchone()
                cursor.execute("SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s)", (message['DOWNchat'], message['DOWNchannel']))
                chat = cursor.fetchone()
                cursor.execute("SELECT id FROM users WHERE username=%s", (username, ))
                user = cursor.fetchone()
                cursor.execute("SELECT id FROM messages WHERE imagemes=%s AND userid=(SELECT id FROM users WHERE username=%s) AND chatid=(SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s)) AND channelid=(SELECT id FROM channels WHERE channelname=%s) ORDER BY id DESC LIMIT 1", ('yes', username, message['DOWNchat'], message['DOWNchannel'], message['DOWNchannel']))
                messageid = cursor.fetchone()
                num = 1000
                find = False
                while find == False:
                    if channel[0] > num:
                        num = num + 1000
                    else:
                        find = True
                path = "usersimages/" + str(num) + "/" + str(channel[0]) + "/" + str(chat[0])
                filename = str(user[0]) + "," + str(messageid[0])
                with open(os.path.join(path, str(filename)), "w+") as fh:
                    fh.write(message['Ifile'])
                emit('usermessage', {'userm': message['data'], 'userfile': message['Ifile'], 'DT': Mestime, 'UPchannel': message['DOWNchannel'], 'UPchat': message['DOWNchat'], 'sender': username, 'PM': 'false', 'file': 'true'}, room=message['DOWNchannel'])
            else:
                emit('usermessage', {'userm': message['data'], 'userfile': "", 'DT': Mestime, 'UPchannel': message['DOWNchannel'], 'UPchat': message['DOWNchat'], 'sender': username, 'PM': 'false', 'file': 'false'}, room=message['DOWNchannel'])

                cursor.execute("INSERT INTO messages (datetime, imagemes, message, userid, chatid, channelid) VALUES(%s, %s, %s, (SELECT id FROM users WHERE username=%s), (SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s)), (SELECT id FROM channels WHERE channelname=%s))", ('no', Mestime, message['data'], username, message['DOWNchat'], message['DOWNchannel'], message['DOWNchannel']))
        if message['DOWNchannel'] != message['UPchannel'] or (message['DOWNchannel'] == message['UPchannel'] and message['DOWNchat'] != message['UPchat']):
            cursor.execute("SELECT lastmesid FROM userlastdata WHERE useid=(SELECT id FROM users WHERE username=%s) AND channelid=(SELECT id FROM channels WHERE channelname=%s) AND chatid=(SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s))", (username, message['UPchannel'], message['UPchat'], message['UPchannel']))
            result = cursor.fetchone()
            if result[0] == 0:
                cursor.execute("SELECT id FROM messages WHERE userid=(SELECT id FROM users WHERE username=%s) AND chatid=(SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s)) AND channelid=(SELECT id FROM channels WHERE channelname=%s) AND datetime=%s", ( message['sender'], message['UPchat'], message['UPchannel'], message['UPchannel'], message['DT'] ))
                result = cursor.fetchone()
                cursor.execute("UPDATE userlastdata SET lastmesid=%s WHERE useid=(SELECT id FROM users WHERE username=%s) AND channelid=(SELECT id FROM channels WHERE channelname=%s) AND chatid=(SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s))", (result[0] ,username, message['UPchannel'], message['UPchat'], message['UPchannel']))  
        else:
            pass
            # emit('usermessage', {'userm': message['data'], 'DT': Mestime, 'UPchannel': message['DOWNchannel'], 'UPchat': message['DOWNchat'], 'sender': username, 'PM': 'false'}, room=message['DOWNchannel'])
    UserIn.commit()
    cursor.close()

@socketio.on('PMjoin', namespace='/test')
def PMjoining_handle(msg):
    cursor = UserIn.cursor()
    username = session['username']    
    cursor.execute("SELECT id FROM users WHERE username=%s", (msg['reciever'], ))
    recieverid = cursor.fetchone()
    cursor.execute("SELECT id FROM users WHERE username=%s", (username, ))       
    senderid = cursor.fetchone()
    cursor.execute("SELECT id FROM PMopen WHERE userid=%s AND openedPM=%s", (senderid[0], recieverid[0]))
    firstresult = cursor.fetchone()
    cursor.execute("SELECT id FROM PMopen WHERE openedPM=%s AND userid=%s", (senderid[0], recieverid[0]))
    secondresult = cursor.fetchone()
    if firstresult or secondresult:
        if secondresult and not firstresult:
            emit("PMexist", {'exist': 'false', 'sender': msg['reciever']})
    elif secondresult and firstresult:
        emit("PMexist", {'exist': 'true'})
    else:
        cursor.execute("INSERT INTO PMopen (openedPM, userid, lastmesid) VALUES(%s, %s, 0)", (senderid[0], recieverid[0]))
        cursor.execute("INSERT INTO PMopen (userid, openedPM, lastmesid) VALUES(%s, %s, 0)", (senderid[0], recieverid[0]))
        Mestime = time.asctime(time.localtime())
        cursor.execute("INSERT INTO PMmessages (datetime, message, senderuserid, recieveruserid) VALUES(%s, %s, %s, %s)", (Mestime, "This is the beginning of everything", senderid[0], recieverid[0]))
        UserIn.commit()
        cursor.close()

@socketio.on('userjoin', namespace='/test')
def join_handle_made(sentroom):
    cursor = UserIn.cursor()
    username = session['username']
    check = False
    if sentroom['select'] == 'channel':
        join_room(sentroom['channel'])
        text = ""
        possible ="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
        while check == False:    
            for x in range(8):
                num = random.randint(0, 61)
                text = text + possible[num]
            cursor.execute("SELECT link FROM channels WHERE link=%s", (text, ))
            if not cursor.fetchall():    
                cursor.execute("INSERT INTO channels (ownerid, channelname, link) VALUES((SELECT id FROM users WHERE username=%s), %s, %s)", (username, sentroom['channel'], text))
                cursor.execute("INSERT INTO userchannels (useid, channelid) VALUES((SELECT id FROM users WHERE username=%s), (SELECT id FROM channels WHERE channelname=%s))", (username, sentroom['channel']))
                UserIn.commit()
                cursor.execute("SELECT id FROM channels where channelname=%s", (sentroom['channel'], ))
                channelid = cursor.fetchone()
                find = False
                num = 1000
                while find == False:
                    if channelid[0] > num:
                        num = num + 1000
                    else:
                        find = True
                channelgroup = num
                path = "usersimages/" + str(channelgroup)
                if not os.path.isdir(path):
                    os.makedirs(path)
                    path = path + "/" + str(channelid[0])
                    if not os.path.isdir(path):
                        os.makedirs(path)
                else:
                    path = path + "/" + str(channelid[0])
                    if not os.path.isdir(path):
                        os.makedirs(path)
                check = True
    elif sentroom['select'] == 'join':
        cursor.execute("SELECT channelname FROM channels WHERE link=%s", (sentroom['link'], ))
        Mestime = time.asctime(time.localtime())
        if not cursor.fetchall():
            emit('confirmjoin', {'select': 'nochannel'})
        else:
            emit('confirmjoin', {'select': 'channel'})
            cursor.execute("SELECT channelname FROM channels WHERE link=%s", (sentroom['link'], ))
            stuff = cursor.fetchone()
            join_room(stuff[0])
            cursor.execute("SELECT id FROM chats WHERE linkid=(SELECT id FROM channels WHERE link=%s)", (sentroom['link'], ))
            chats = cursor.fetchall()
            for items in chats:
                cursor.execute("INSERT INTO userlastdata (useid, channelid, chatid) VALUES((SELECT id FROM users WHERE username=%s), (SELECT id FROM channels WHERE link=%s), %s)", (username, sentroom['link'], items[0]))
            cursor.execute("INSERT INTO userchannels (useid, channelid) VALUES((SELECT id FROM users WHERE username=%s), (SELECT id FROM channels WHERE link=%s))", (username, sentroom['link']))
            cursor.execute("SELECT channelname FROM channels WHERE link=%s", (sentroom['link'], ))
            stuff = cursor.fetchone()
            cursor.execute("SELECT id FROM chats WHERE linkid=(SELECT id FROM channels WHERE channelname=%s) LIMIT 1", (stuff[0], ))
            joinchat = cursor.fetchone()
            cursor.execute("INSERT INTO messages (datetime, message, userid, chatid, channelid) VALUES(%s, %s, (SELECT id FROM users WHERE username=%s), %s, (SELECT id FROM channels WHERE channelname=%s))", (Mestime, username + ' has joined', username, joinchat[0], stuff[0]))
            emit('userdata', {'data': stuff[0], 'sentdata': 'channel', 'owner': 'false', 'join': 'true'})
    else:
        cursor.execute("INSERT INTO chats (chatname, linkid) VALUES(%s, (SELECT id FROM channels WHERE channelname=%s))", (sentroom['chatname'], sentroom['channel']))
        UserIn.commit()
        cursor.execute("SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s)", (sentroom['chat'], sentroom['channel']))
        chatid = cursor.fetchone()
        cursor.execute("SELECT id FROM channels WHERE channelname=%s", (sentroom['channel'], ))
        channelid = cursor.fetchone()
        check = False
        num = 1000
        while check == False:
            if channelid[0] > num:
                num = num + 1000
            else: 
                check = True
        path = "usersimages/" + str(num) + "/" + str(channelid[0]) + "/" + str(chatid[0])
        if not os.path.isdir(path):
            os.makedirs(path)
        Mestime = time.asctime(time.localtime())
        cursor.execute("INSERT INTO messages (datetime, message, userid, chatid, channelid) VALUES(%s, %s, (SELECT id FROM users WHERE username=%s), (SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s)), (SELECT id FROM channels WHERE channelname=%s))", (Mestime, "This is the beginning of everything.", username, sentroom['chatname'], sentroom['channel'], sentroom['channel']))
        cursor.execute("SELECT useid FROM userchannels WHERE channelid=(SELECT id FROM channels WHERE channelname=%s)", (sentroom['channel'], ))
        users = cursor.fetchall()
        for items in users:
            cursor.execute("INSERT INTO userlastdata (useid, channelid, chatid) VALUES(%s, (SELECT id FROM channels WHERE channelname=%s), (SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s)))", (items[0], sentroom['channel'], sentroom['chatname'], sentroom['channel']))
    UserIn.commit()
    cursor.close()

@socketio.on('userleave', namespace="/test")
def leave_handler(data):
    cursor = UserIn.cursor()
    username = session['username']
    cursor.execute("DELETE FROM userlastdata WHERE channelid=(SELECT id FROM channels WHERE channelname=%s) AND useid=(SELECT id FROM users WHERE username=%s)", (data['channel'], username))
    cursor.execute("DELETE FROM userchannels WHERE useid=(SELECT id FROM users WHERE username=%s) AND channelid=(SELECT id FROM channels WHERE channelname=%s)", (username, data['channel']))
    leave_room(data['channel'])    
    UserIn.commit()
    cursor.close()

@socketio.on('userdelete', namespace="/test")
def delete_handler(data):
    cursor = UserIn.cursor()
    if data['select'] == 'channel':
        cursor.execute("SELECT id FROM channels WHERE channelname=%s", (data['channel'], ))
        channelid = cursor.fetchone()
        check = False
        num = 1000
        while check == False:
            if channelid[0] > num:
                num = num + 1000
            else: 
                check = True        
        path = "usersimages/" + str(num) + "/" + str(channelid[0])
        shutil.rmtree(path)
        cursor.execute("DELETE FROM userlastdata WHERE channelid=(SELECT id FROM channels WHERE channelname=%s)", (data['channel'], ))
        cursor.execute("DELETE FROM userchannels WHERE channelid=(SELECT id FROM channels WHERE channelname=%s)", (data['channel'], ))
        cursor.execute("DELETE FROM messages WHERE channelid=(SELECT id FROM channels WHERE channelname=%s)", (data['channel'], ))
        cursor.execute("DELETE FROM chats WHERE linkid=(SELECT id FROM channels WHERE channelname=%s)", (data['channel'], ))
        cursor.execute("DELETE FROM channels WHERE channelname=%s", (data['channel'], ))

    if data['select'] == 'chat':
        cursor.execute("SELECT id FROM channels WHERE channelname=%s", (data['channel'], ))
        channelid = cursor.fetchone()
        cursor.execute("SELECT id FROM chats WHERE chatname=%s AND linkid=%s", (data['chat'], channelid[0]))
        chatid = cursor.fetchone()
        check = False
        num = 1000
        while check == False:
            if channelid[0] > num:
                num = num + 1000
            else: 
                check = True        
        path = "usersimages/" + str(num) + "/" + str(channelid[0]) + "/" + str(chatid[0])
        shutil.rmtree(path)       
        cursor.execute("DELETE FROM userlastdata WHERE channelid=(SELECT id FROM channels WHERE channelname=%s) AND chatid=(SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s))", (data['channel'], data['chat'], data['channel']))
        cursor.execute("DELETE FROM messages WHERE channelid=(SELECT id FROM channels WHERE channelname=%s) AND chatid=(SELECT id FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s))", (data['channel'], data['chat'], data['channel']))
        cursor.execute("DELETE FROM chats WHERE chatname=%s AND linkid=(SELECT id FROM channels WHERE channelname=%s)", (data['chat'], data['channel']))
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
    cursor.execute("INSERT INTO users (username, password, confirmpassword, userPMid) VALUES(%s, %s, %s, %s);", (request.form["SUsername"], request.form["SPassword"], request.form["SCPassword"], 0))
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
        
    return html
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=80)    