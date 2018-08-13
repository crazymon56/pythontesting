from flask import Flask, request, redirect, url_for, session
from redis import Redis, RedisError
import os
import socket
import codecs
from flask_socketio import SocketIO
import mysql.connector 

# Connect to Redis
redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

app = Flask(__name__)
app.config['SECRET_KEY'] = "slwol;ayesal."
socketio = SocketIO(app)

UserIn = mysql.connector.connect("localhost", "root", "password", "userinformation")
cursor = UserIn.cursor()


Userinfo = list()
#Chat
@app.route("/BlahChat/" + UserN, methods=['POST', 'GET'])
def chat():
    pass


#SigningUp
@app.route("/SignUpCon", methods=['POST', 'GET'])
def signup():
    UserN = request.form['SUsername']
    UserP = request.form['SPassword']
    UserCP = request.form['SCPassword']
    try:
        cursor.execute(
        """
        IF (SELECT username FROM user WHERE username = %s) 
        THEN 
        ELSE
        THEN INSERT INTO user VALUES (%s,%s,%s)
        END IF
        """
        ,(UserN, UserN, UserP, UserCP))
        UserIn.commit()
        UserIn.close()
    except:
        UserIn.rollback()
        UserIn.close()
    if UserP != UserCP:
        with open('Signup.html', 'r') as fh:        
            html = fh.read()
        return html
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
    UserN = request.form['LUsername']
    UserP = request.form['LPassword']
    usercheck = False  
    if request.method == 'POST':
        session['username'] = UserN 
        for x  in Userinfo:
            data = x.split(",")
            ChUN = data[0]
            ChUP = data[1]
            if UserN == ChUN:
                if UserP == ChUP:
                    usercheck = True
                    with open('Chat.html', 'r') as fh:        
                        html = fh.read()
                    return html     
        if usercheck == False:
            with open('Invalidlogin.html', 'r') as fh:        
                usercheck = False
                html = fh.read()        
            return html                   

#SignUp
@app.route("/", methods=['GET', 'POST'])
def index():

    with open('Signup.html', 'r') as fh:
        html = fh.read()
        
    return html
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)   
    socketio.run(app)    