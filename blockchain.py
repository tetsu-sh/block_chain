import logging
import sys
import time
import utils
import json,hashlib
import hashlib
from ecdsa import NIST256p
from ecdsa import VerifyingKey
MINING_DIFFICULTY=3
MINING_SENDER = "THE BLOCKCHAIN"
MINING_REWARD = 1.0

logging.basicConfig(level=logging.INFO,stream=sys.stdout)
logger = logging.getLogger(__name__)

class BlockChain(object):

    def __init__(self,blockchain_adress=None):
       self.transaction_pool = []
       self.chain = []
       self.create_block(0,self.hash({}))
       self.blockchain_adress = blockchain_adress 

    def create_block(self, nonce,previous_hash):
        block = utils.sorted_dict_by_key({
            "timestamp" : time.time(),
            "transactions" : self.transaction_pool,
            "nonce" : nonce,
            "previous_hash" : previous_hash
        })
        self.chain.append(block)
        self.transaction_pool = []
        return block

    def hash(self,block):
        sorted_block = json.dumps(block,sort_keys=True)
        return hashlib.sha256(sorted_block.encode()).hexdigest()

    def add_transaction(self,sender_blockchain_adress,recipient_blockchain_adress,value,sender_public_key=None,signature=None):
        transaction =utils.sorted_dict_by_key({
          "sender_blockchain_adress":sender_blockchain_adress,
          "recipient_blockchain_adress":recipient_blockchain_adress,
          "value":float(value)  
        })
        if sender_blockchain_adress ==MINING_SENDER:
            self.transaction_pool.append(transaction)
            return True
        if self.verify_transaction_signature(sender_public_key,signature,transaction):
            self.transaction_pool.append(transaction)
            return True
        return False

    def verify_transaction_signature(self,sender_public_key,signature,transaction):
        sha256 = hashlib.sha256()
        sha256.update(str(transaction).encode("utf-8"))
        message = sha256.digest()
        signature_bytes = bytes().fromhex(signature)
        verifying_key = VerifyingKey.from_string(
            bytes().fromhex(sender_public_key),curve=NIST256p
        )
        verified_key = verifying_key.verify(signature_bytes,message)
        return verified_key

    def valid_proof(self,transactions,previous_hash,nonce,difficulty=MINING_DIFFICULTY):
        guess_block = utils.sorted_dict_by_key({
            "transactions":transactions,
            "nonce":nonce,
            "previous_hash":previous_hash
        })
        guess_hash=self.hash(guess_block)
        return guess_hash[:difficulty] == "0"*difficulty

    def proof_work(self):
        transactions = self.transaction_pool.copy()
        previous_hash = self.hash(self.chain[-1])
        nonce = 0
        while self.valid_proof(transactions,previous_hash,nonce) is False:
            nonce += 1
        return nonce

    def mining(self):
        self.add_transaction(
            sender_blockchain_adress = MINING_SENDER,
            recipient_blockchain_adress = self.blockchain_adress,
            value = MINING_REWARD
        )
        nonce = self.proof_work()
        previous_hash = self.hash(self.chain[-1])
        self.create_block(nonce,previous_hash)
        logger.info({"action":"mining","status":"success"})
        return True
    def caluculate_total_amount(self,block_chain_adress):
        total_amount = 0.0
        for block in self.chain:
            for transaction in block["transactions"]:
                value = float(transaction["value"])
                if block_chain_adress == transaction["recipient_blockchain_adress"]:
                    total_amount +=value
                if block_chain_adress == transaction["sender_blockchain_adress"]:
                    total_amount -= value
        return total_amount

if __name__ == "__main__":
    my_blockchain_address ="my_blockchain_address"
    block_chain = BlockChain(blockchain_adress=my_blockchain_address)
    utils.pprint(block_chain.chain)

    block_chain.add_transaction("A","B",1.0)
    block_chain.mining()
    utils.pprint(block_chain.chain)

    block_chain.add_transaction("C","D",2.0)
    block_chain.add_transaction("X","Y",3.0)
    block_chain.mining()
    utils.pprint(block_chain.chain)

    print("my",block_chain.caluculate_total_amount(my_blockchain_address))
    print("C",block_chain.caluculate_total_amount("C"))



