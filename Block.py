from time import time
import json
import hashlib


class Block:

    def __init__(self, p_index, p_transactions, p_previous_hash):
        self.index = p_index
        self.date = time()
        self.transactions = p_transactions
        self.previous_hash = p_previous_hash
        self.nonce = 0

    def hash(self):
        """
        Crée un hash sha256 à partir des données du block
        :return: <str> un hash sha256 à partir du json de l'objet
        """
        block_string = self.jsonify().encode()
        return hashlib.sha256(block_string).hexdigest()

    def jsonify(self):
        """
        Crée une version json de l'objet
        :return: <str> json de l'objet
        """
        return json.dumps(self.__dict__, sort_keys=True)

    def proof_of_work(self, p_difficulte):
        """
        Valide la preuve : est-ce que hash() commence par DIFFICULTE zéros ?
        :param p_last_proof: <int> Preuve précédente dans la chaine
        :param p_proof: <int> Preuve courante
        :return: <bool> True si la preuve est correcte, False sinon
        """
        return self.hash()[:p_difficulte] == "0" * p_difficulte

    def miner(self, p_difficulte):
        """
        Preuve de travail :
        - Trouver un nombre p' tel que hash(pp') commence par DIFFICULTE zéros consécutifs.
        - p est la preuve précédente de la chaine et p' est la nouvelle preuve
        :param p_last_proof: <int> dernière preuve de la chaine
        :return: <int> la nouvelle preuve vérifiant hash(pp') commence par 4 zéros
        """
        self.nonce = 0
        while not self.proof_of_work(p_difficulte):
            self.nonce += 1
