from time import time
import json
import hashlib


class Block:

    def __init__(self, p_index, p_transactions, p_previous_hash, p_proof):
        self.index = p_index
        self.date = time()
        self.transactions = p_transactions
        self.previous_hash = p_previous_hash
        self.proof = p_proof

    """
    Crée un hash sha256 à partir des données du block
    :return: <str> un hash sha256 à partir du json de l'objet
    """
    def hash(self):
        block_string = self.jsonify().encode()
        return hashlib.sha256(block_string).hexdigest()

    """
    Crée une version json de l'objet
    :return: <str> json de l'objet
    """
    def jsonify(self):
        return json.dumps(self.__dict__, sort_keys=True)
