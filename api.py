from uuid import uuid4
from BlockChain import BlockChain
from flask import Flask, request, jsonify

app = Flask(__name__)

# Identification du noeud
node_identifier = str(uuid4()).replace('-', '')

# Création de la blockchain
blockchain = BlockChain()


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Ajoute la transaction à la liste des pending transactions
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'La transaction sera ajoutée au block {index}'}
    return jsonify(response), 201


@app.route('/mine', methods=['GET'])
def mine():
    # Miner consiste à faire tourner l'algorithme de preuve de travail
    # Celui-ci tourne à partir de la 'preuve' du dernier bloc de la chaine
    last_block = blockchain.last_block
    last_proof = last_block.proof
    proof = blockchain.proof_of_work(last_proof)

    # Ajoute la transaction "récompense" pour avoir bien miné
    blockchain.new_transaction(
        p_sender="0",
        p_recipient=node_identifier,
        p_amount=1,
    )

    # Génère le bloc à partir des transactions en attente
    previous_hash = last_block.hash()
    block = blockchain.new_block(p_previous_hash=previous_hash, p_proof=proof)

    response = {
        'message': "New Block Forged",
        'index': block.index,
        'transactions': block.transactions,
        'proof': block.proof,
        'previous_hash': block.previous_hash
    }

    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.json_chain,
        'length': len(blockchain.block_chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: il faut une véritable liste de noeuds", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'Les noeuds ont été ajoutés',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'La chaine a été remplacée',
            'new_chain': blockchain.block_chain
        }
    else:
        response = {
            'message': 'La chaine est déjà la référence',
            'chain': blockchain.block_chain
        }

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
