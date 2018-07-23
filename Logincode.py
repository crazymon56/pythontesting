from flask import Flask, request
from redis import Redis, RedisError
import os
import socket
import codecs

# Connect to Redis
redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

app = Flask(__name__)

@app.route("/lgggg")
def yeeess():
    pass

##Login
@app.route("/")
def hello():
    with open('Login.html', 'r') as fh:
        html = fh.read()
   
    if request.form.get('Username') == 'Chris':
        login()
    elif request.form.get('Username') != 'Chris':
        with open ('Invalidlogin.html', 'r') as fh:
            html = fh.read()
    else:
        pass
        
    return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname())
    if __name__ == "__main__":
        app.run(host='0.0.0.0', port=80)   