from uuid import uuid4
from BlockChain import BlockChain
from flask import Flask, request, jsonify

app = Flask(__name__)

# Identification du noeud
node_identifier = str(uuid4()).replace('-', '')

# Création de la blockchain
blockchain = BlockChain()


@app.route('/transactions', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Ajoute la transaction à la liste des transactions en attente
    blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': 'La transaction est en attente'}
    return jsonify(response), 201


@app.route('/blocks', methods=['POST'])
def new_block():
    block = blockchain.add_block()

    return block.jsonify(), 201


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
