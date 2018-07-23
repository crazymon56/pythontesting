from flask import Flask, request
from redis import Redis, RedisError
import os
import socket
import codecs
# Connect to Redis
redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

app = Flask(__name__)

@app.route('/login')
def login():
    if request.form.get('Username') == 'Chris':
        
    pass

@app.route("/")
def hello():
    with open('looks.html', 'r') as fh:
        html = fh.read()
    
    return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname())
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

