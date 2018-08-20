from flask import Flask, request, redirect, url_for, session, render_template
from redis import Redis, RedisError
import os
import socket
import codecs
from flask_socketio import SocketIO, send, emit
import mysql.connector 
import json

# Connect to Redis
redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

app = Flask(__name__)
app.config['SECRET_KEY'] = "slwol;ayesal."
socketio = SocketIO(app)

UserIn = mysql.connector.connect(user="root", db="userinformation", passwd="passwordfun", host="mysqldb")



#Chat
@app.route("/BlahChat", methods=['POST', 'GET'])
def chat():
    if(session['username'] == ''):
        return 'Username already taken'
    else:
        with open('Chat.html', 'r') as fh:        
            html = fh.read()
        return html

@socketio.on('json')
def handle_message(message):

    emit("usermessage", {'data' : str(json)})

#SigningUp
@app.route("/SignUpCon", methods=['POST', 'GET'])
def signup():
    cursor = UserIn.cursor()
    if request.form['SPassword'] != request.form['SCPassword']:
        with open('Signup.html', 'r') as fh:        
            html = fh.read()
        return html
    
    cursor.execute("INSERT INTO user (username, password, confirmpassword) VALUES(%s, %s, %s);", (request.form["SUsername"], request.form["SPassword"], request.form["SCPassword"]))
    UserIn.commit()
    cursor.close()

    
    with open('Signupcon.html', 'r') as fh:        
        html = fh.read()
    return html

#Logout
@app.route("/Logout", methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('Login'))        

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
    try:
        if request.method == 'POST':
            session['username'] = request.form['LUsername'] 
            cursor.execute("SELECT username, password FROM user")
            for items in cursor:
                if(items[0] == request.form['LUsername']):
                    if(items[1] == request.form['LPassword']):
                        return redirect('BlahChat') 
                        cursor.close()      
    except:
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
    app.run(host='0.0.0.0', port=80)   
    socketio.run(app)    