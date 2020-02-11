from flask import Flask,jsonify
import wallet
import blockchain

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "hello world"

if __name__=="__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-p","--port",default=5000,type=int,help="port listen on")
    args = parser.parse_args()
    port = args.port

    app.run(host="0.0.0.0",port = port,threaded=True,debug=True)