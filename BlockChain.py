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
        block = Block(p_index=1, p_transactions=[], p_previous_hash=None)
        self.block_chain.append(block)

    @property
    def last_block(self):
        return self.block_chain[-1]

    @property
    def last_index(self):
        return len(self.block_chain)

    @property
    def json_chain(self):
        return [block.jsonify() for block in self.block_chain]

    def new_transaction(self, p_sender, p_recipient, p_amount):
        """
        Soumet une nouvelle transaction à la chaine
        :param p_sender: <str> L'adresse de l'expediteur
        :param p_recipient: <str> L'adresse du bénéficiaire
        :param p_amount: <int> Montant
        :return: <int> L'index du bloc qui va porter la transaction
        """
        self.pending_transactions.append({
            'sender': p_sender,
            'recipient': p_recipient,
            'amount': p_amount
        })
        return self.last_block.index + 1

    def add_block(self):
        """
        Ajoute un bloc à la chaine, contenant les transactions en attente
        :return: le bloc ajouté
        """
        block = Block(p_index=self.last_index + 1, p_transactions=self.pending_transactions,
                      p_previous_hash=self.last_block.hash())
        block.miner(self.DIFFICULTE)

        self.block_chain.append(block)
        self.pending_transactions = []
        return block

    def register_node(self, p_address):
        """
        Ajoute un noeud à la liste des noeuds connus
        :param p_address: <str> Address d'un noeud. Eg. 'http://192.168.0.5:5000'
        :return: None
        """
        parsed_url = urlparse(p_address)
        self.nodes.add(parsed_url.netloc)

    @staticmethod
    def is_firstblock_valid(p_chain):
        first_block = p_chain[0]

        if first_block.index != 1:
            return False

        if first_block.previous_hash is not None:
            return False

        return True

    @staticmethod
    def is_block_valid(p_block, p_previous_block):
        if p_block.index != p_previous_block.index + 1:
            return False

        if p_block.previous_hash != p_previous_block.hash():
            return False

        return True

    @staticmethod
    def valid_chain(p_chain):
        """
        Vérifie la validité d'une blockchain complète
        :param p_chain: <list> Une blockchaine
        :return: <bool> True si chain est valide, False sinon
        """
        if not BlockChain.is_firstblock_valid(p_chain):
            return False

        current_index = 1
        while current_index < len(p_chain):
            block = p_chain[current_index]
            last_block = p_chain[current_index - 1]
            if not BlockChain.is_block_valid(block, last_block):
                return False
            current_index += 1
        return True

    def resolve_conflicts(self):
        """
        Algo de consensus : remplace la chaine par la plus longue chaine valide du réseau
        :return: <bool> True si la chaine est remplacée, False sinon
        """
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
