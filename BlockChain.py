import hashlib
from urllib.parse import urlparse
import requests
from Block import Block


class BlockChain:

    DIFFICULTE = 4

    def __init__(self):
        # Initialisation des attributs
        self.block_chain = []
        self.pending_transactions = []
        self.nodes = set()

        # Création du block initial
        block = Block(p_index=1, p_transactions=self.pending_transactions, p_previous_hash=1, p_proof=100)
        self.block_chain.append(block)

    @property
    def last_block(self):
        return self.block_chain[-1]

    @property
    def json_chain(self):
        return [block.jsonify() for block in self.block_chain]

    """
    Soumet une nouvelle transaction à la chaine
    :param sender: <str> L'adresse de l'expediteur
    :param recipient: <str> L'adresse du bénéficiaire
    :param amount: <int> Montant
    :return: <int> L'index du bloc qui va porter la transaction
    """
    def new_transaction(self, p_sender, p_recipient, p_amount):
        self.pending_transactions.append({
            'sender': p_sender,
            'recipient': p_recipient,
            'amount': p_amount
        })
        return self.last_block.index + 1

    def new_block(self, p_previous_hash, p_proof=100):
        block = Block(p_index=len(self.block_chain) + 1, p_transactions=self.pending_transactions,
                      p_previous_hash=p_previous_hash, p_proof=p_proof)
        self.block_chain.append(block)
        self.pending_transactions = []
        return self.last_block

    """
    Preuve de travail :
    - Trouver un nombre p' tel que hash(pp') commence par 4 zéros consécutifs.
    - p est la preuve précédente de la chaine et p' est la nouvelle preuve
    :param last_proof: <int> dernière preuve de la chaine
    :return: <int> la nouvelle preuve vérifiant hash(pp') commence par 4 zéros
    """
    def proof_of_work(self, p_last_proof):
        proof = 0
        while self.valid_proof(p_last_proof, proof) is False:
            proof += 1
        return proof

    """
    Valide la preuve : est-ce que hash(last_proof, proof) commence par 4 zéros ?
    :param last_proof: <int> Preuve précédente dans la chaine
    :param proof: <int> Preuve courante
    :return: <bool> True si la preuve est correcte, False sinon
    """
    @staticmethod
    def valid_proof(p_last_proof, p_proof):
        guess = f'{p_last_proof}{p_proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:BlockChain.DIFFICULTE] == "0" * BlockChain.DIFFICULTE

    """
    Ajoute un noeud à la liste des noeuds connus
    :param address: <str> Address d'un noeud. Eg. 'http://192.168.0.5:5000'
    :return: None
    """
    def register_node(self, p_address):
        parsed_url = urlparse(p_address)
        self.nodes.add(parsed_url.netloc)

    """
    Vérifie la validité d'une blockchain complète
    :param chain: <list> Une blockchaine
    :return: <bool> True si chain est valide, False sinon
    """
    @staticmethod
    def valid_chain(p_chain):
        last_block = p_chain[0]
        current_index = 1
        while current_index < len(p_chain):
            block = p_chain[current_index]

            # Vérifie que le hash du block est correct
            if block['previous_hash'] != last_block.hash():
                return False

            # Vérifie que la preuve est correcte
            if not BlockChain.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1
        return True

    """
    Algo de consensus : remplace la chaine par la plus longue chaine valide du réseau
    :return: <bool> True si la chaine est remplacée, False sinon
    """
    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        # On valide uniquement les chaines plus longues que celle du noeud
        max_length = len(self.block_chain)

        # Récupère les chaines des noeuds connus
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Vérifie la longueur et la validité de la chaine
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Le cas échéant, effectue le remplacement
        if new_chain:
            self.block_chain = new_chain
            return True

        return False
