from flask import Flask
from redis import Redis, RedisError
import os
import socket

# Connect to Redis
redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

app = Flask(__name__)

@app.route("/")
def hello():

    html = "<h1><center>Chat</center></h1>" \
	   "<h1><center>Login</center></h1>" \
	   "<form>" \
	   "<h3><center>Username</center></h3>" \
	   "<center><input type=text name=Username value=JohnDoe></center><br>" \
	   "<h3><center>Password</center></h3>" \
	   "<center><input type=text name=Password value=JohnDoe1></center><br>" \
	   "<center><input type=submit class=submit value=Login></center>" \
	   "</form>"   
    return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname())
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

