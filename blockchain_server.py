from flask import Flask,jsonify
import wallet
import blockchain

app = Flask(__name__)
cache = {}
def get_blockchain():
    cached_blockchain = cache.get("blockchain")
    if not cached_blockchain:
        miners_wallet = wallet.Wallet()
        cache["blockchain"] =blockchain.BlockChain(
            blockchain_adress=miners_wallet.blockchain_adress,
            port=app.config["port"])
        app.logger.warning({
            "private_key":miners_wallet.private_key,
            "public_key":miners_wallet.public_key,
            "blockchain_adress":miners_wallet.blockchain_adress
        }
        )
    return cache["blockchain"]    

@app.route("/chain",methods=["GET"])
def get_chain():
    blockchain = get_blockchain()
    response ={
        "chain":blockchain.chain
    } 
    
    return jsonify(response),200

if __name__=="__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-p","--port",default=5000,type=int,help="port listen on")
    args = parser.parse_args()
    port = args.port

    app.config["port"] = port

    app.run(host="0.0.0.0",port = port,threaded=True,debug=True)