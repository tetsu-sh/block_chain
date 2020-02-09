from ecdsa import NIST256p
from ecdsa import SigningKey
import codecs
import base58
import hashlib
import utils

class Wallet():

    def __init__(self):
        self._private_key = SigningKey.generate(curve=NIST256p)
        self._public_key = self._private_key.get_verifying_key()
        self. _blockchain_adress = self.generate_blockchain_adress()
    
    @property
    def private_key(self):
        return self._private_key.to_string().hex()
    
    @property
    def public_key(self):
        return self._public_key.to_string().hex()

    @property
    def blockchain_adress(self):
        return self._blockchain_adress

    def generate_blockchain_adress(self):
        public_key_bytes = self._public_key.to_string()
        sha256_bpk = hashlib.sha256(public_key_bytes)
        sha256_bpk_digest = sha256_bpk.digest()

        ripemd160_bpk = hashlib.new("ripemd160")
        ripemd160_bpk.update(sha256_bpk_digest)
        ripemd160_bpk_digest = ripemd160_bpk.digest()
        ripemd160_bpk_hex = codecs.encode(ripemd160_bpk_digest,"hex")

        network_byte = b"00"
        network_bitcoin_public_key = network_byte + ripemd160_bpk_hex
        network_bitcoin_public_key_bytes = codecs.decode(network_bitcoin_public_key,"hex")

        sha256_bpk = hashlib.sha256(network_bitcoin_public_key_bytes)
        sha256_bpk_digest = sha256_bpk.digest()
        sha256_2_nbpk = hashlib.sha256(sha256_bpk_digest)
        sha256_2_nbpk_digest = sha256_2_nbpk.digest()
        sha256_hex = codecs.encode(sha256_2_nbpk_digest,"hex")

        checksum = sha256_hex[:8]

        address_hex = (network_bitcoin_public_key + checksum).decode("utf-8")

        blockchain_adress =base58.b58encode(address_hex).decode("utf-8")
        return blockchain_adress

class Transaction():
    def __init__(self,sender_private_key,sender_public_key,sender_blockchain_adress,recipient_blockchain_adress,value):
        self.sender_private_key =sender_private_key
        self.sender_public_key = sender_public_key
        self.sender_blockchain_adress = sender_blockchain_adress
        self.recipient_blockchain_adress = recipient_blockchain_adress
        self.value = value
    def generate_signature(self):
        sha256 = hashlib.sha256()
        transaction = utils.sorted_dict_by_key({
            "sender_blockchain_adress":self.sender_blockchain_adress,
            "recipient_blockchain_adress":self.recipient_blockchain_adress,
            "value": float(self.value)
        })
        sha256.update(str(transaction).encode("utf-8"))
        message = sha256.digest()
        private_key = SigningKey.from_string(
            bytes().fromhex(self.sender_private_key),curve=NIST256p)
        private_key_sign=private_key.sign(message)
        signature = private_key_sign.hex()
        return signature
    
if __name__=="__main__":
    wallet_M = Wallet()
    wallet_A = Wallet()
    wallet_B = Wallet()
    t = Transaction(wallet_A.private_key,wallet_A.public_key,wallet_A.blockchain_adress,wallet_B.blockchain_adress,1.0)

    ####################Blockchain node
    import blockchain
    block_chain = blockchain.BlockChain(
        blockchain_adress = wallet_M.blockchain_adress)
    is_added = block_chain.add_transaction(
        wallet_A.blockchain_adress,wallet_B.blockchain_adress,1.0,wallet_A.public_key,t.generate_signature()
    )
    print("is_added?",is_added)
    block_chain.mining()
    utils.pprint(block_chain.chain)

    print("A",block_chain.caluculate_total_amount(wallet_A.blockchain_adress))
    print("B",block_chain.caluculate_total_amount(wallet_B.blockchain_adress))
    print("M",block_chain.caluculate_total_amount(wallet_M.blockchain_adress))