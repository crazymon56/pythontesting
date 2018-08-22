from flask import Flask, request, redirect, url_for, session, render_template
from flask_socketio import SocketIO, emit
import os
import socket
import codecs
import mysql.connector 


app = Flask(__name__)
app.config['SECRET_KEY'] = "slwol;ayesal."
socketio = SocketIO(app)

UserIn = mysql.connector.connect(user="root", db="userinformation", passwd="passwordfun", host="mysqldb")



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
    emit('username', {'data' : session['username']})

@socketio.on('useresponse', namespace='/test')
def message_handle(message):
    emit('usermessage', {'data': message['data']})

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
        validlog = False 
        cursor.execute("SELECT username, password FROM user label: LOOP IF user[0] == %s AND user[1] == %s THEN SET %s = TRUE END IF; LEAVE label; END LOOP label;", (request.form['LUsername'], request.form['LPassword'], validlog))
        

        # for items in cursor:
        #     if(items[0] == request.form['LUsername'] and items[1] == request.form['LPassword']):
        #         validlog = True

        cursor.close()
        print(validlog)        
        if(validlog == True):
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