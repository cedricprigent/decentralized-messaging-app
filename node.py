from hashlib import sha256
import json
import time
import datetime
import network_details

from blockchain import *

from flask import Flask, request
import requests, socket

host_address = network_details.get_ip_address_2()

# Initialisation de l'application Flask
app = Flask(__name__)

# Initialisation de la blockchain
blockchain = Blockchain()

#Ajout d'une transaction
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["author", "content"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

    tx_data["timestamp"] = time.time()

    blockchain.add_new_transaction(tx_data)

    return "Success", 201

#Récupération de la chaîne et des pairs
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    peers_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
        
    for peer in peers:
        if peer.startswith("http"):
            peer = (peer.split("//")[1]).split(':')[0]

        peers_data.append(peer)

    return json.dumps({ "length": len(chain_data),
                        "chain" : chain_data,
                        "peers" : peers_data})

#Minage d'un bloc
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transaction to mine"
    #else:
        #On vérifie que l'on ai la chaîne la plus longue du réseau
        #chain_length = len(blockchain.chain)
        #consensus()
        #if chain_length == len(blockchain.chain):
        #    announce_new_block(blockchain.last_block)

    return "Block #{} is mined".format(blockchain.last_block.index)

#Récupération des transactions non validées
@app.route('/pending_transactions')
def get_pending_transactions():
    return json.dumps(blockchain.unconfirmed_transactions)

#Liste des noeuds du réseau
peers = set()
peers.add(host_address)

#Enregistre un nouveau noeud au réseau
#Lui envoie la chaîne mise à jour
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    if node_address.startswith("http"):
        node_adress = (node_address.split("//")[1]).split(':')[0]

    peers.add(node_address)

    #Retourne la blockchain au nouveau noeud enregistré pour qu'il se synchronise
    return get_chain()

#Enregistrement au réseau
#Récupération de la chaîne mise à jour
@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    #Demande d'entregistrement à un noeud distant
    response = requests.post(node_address + "/register_node",
                            data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        #Mise à jour de la chaîne et des pairs
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        return response.content, response.status_code

def create_chain_from_dump(chain_dump):
    blockchain = None
    for idx, block_data in enumerate(chain_dump):
        if blockchain == None:
            genesis_block = Block(  block_data["index"],
                                    block_data["transactions"],
                                    block_data["timestamp"],
                                    block_data["previous_hash"])
            genesis_block.hash = block_data['hash']
            genesis_block.nonce = 0
            blockchain = Blockchain(genesis_block)
        else:
            block = Block(  block_data["index"],
                            block_data["transactions"],
                            block_data["timestamp"],
                            block_data["previous_hash"])
            block.nonce = block_data['nonce']
            proof = block_data['hash']
            if idx > 0:
                added = blockchain.add_block(block, proof)
                if not added:
                    raise Exception("The chain dump is tampered")
            else:
                blockchain.chain.append(block)
    return blockchain


#Algorithme de consensus
#Si une chaîne plus longue est trouvée, remplace la chaîne courante par celle-ci
def consensus():
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get('http://{}:8000/chain'.format(node))

        length = response.json()['length']
        chain = response.json()['chain']

        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False

#Vérifie et ajoute un bloc qui vient d'être miné par un autre noeud
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(  block_data["index"],
                    block_data["transactions"],
                    block_data["timestamp"],
                    block_data["previous_hash"],
                    block_data["nonce"])

    #block.hash= block_data['hash']
    proof = block_data['hash']
    added = blockchain.add_block(block, proof)
    #blockchain.chain.append(block)
    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201

#Prévient les autres noeuds du nouveau bloc miné
def announce_new_block(block):
    
    for peer in peers:
            if peer == host_address:
                continue
            url = "http://{}:8000/add_block".format(peer)
            headers = {'Content-Type': "application/json"}
            requests.post(url,
                        data=json.dumps(block.__dict__, sort_keys=True),
                        headers=headers)
