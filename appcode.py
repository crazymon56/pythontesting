from flask import Flask, request, redirect, url_for, session
from redis import Redis, RedisError
import os
import socket
import codecs

# Connect to Redis
redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

app = Flask(__name__)

app.secret_key = 'k4k29_dk!!ko'
Userinfo = list()
#Signing Up
@app.route("/SignUp", methods=['POST', 'GET'])
def signup():
    Userinfo.append(request.form['SUsername'] + ',' + request.form['SPassword'])
    UserP = request.form['SPassword']
    UserCP = request.form['SCPassword']
    if UserP != UserCP:
        with open('Signup.html', 'r') as fh:        
            html = fh.read()
        return html
    with open('Signupcon.html', 'r') as fh:        
        html = fh.read()
        return html

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

# Login
@app.route("/", methods=['GET', 'POST'])
def index():

    with open('Signup.html', 'r') as fh:
        html = fh.read()
        
    return html
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)       