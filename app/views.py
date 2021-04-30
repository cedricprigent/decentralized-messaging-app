import datetime
import json
import network_details

import requests, socket
from flask import render_template, redirect, request

from app import app

# The node with which our application interacts, there can be multiple
# such nodes as well.

host_address = network_details.get_ip_address_2()
CONNECTED_NODE_ADDRESS = "http://"+host_address+":8000"

posts = []
blocks = []
peers = []


def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)

def fetch_blocks():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            content.append(block)

        global blocks
        blocks = sorted(content, key=lambda k: k['index'],
                       reverse=True)

def fetch_peers():
    """
    Function to fetch the peers from a blockchain node
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for peer in chain["peers"]:
            content.append(peer)

        global peers
        peers = sorted(content)

@app.route('/')
def index():
    fetch_peers()
    fetch_posts()
    fetch_blocks()
    return render_template('index.html',
                           title='Application Blockchain: Messagerie '
                                 'Décentralisée - '+host_address,
                           peers=peers,
                           posts=posts,
                           blocks=blocks,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


@app.route('/submit_transaction', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application
    """
    post_content = request.form["content"]
    author = request.form["author"]

    post_object = {
        'author': author,
        'content': post_content,
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/')

@app.route('/submit_address', methods=['POST'])
def submit_ip():
    """
    Endpoint to connect to a new network via our application
    """

    ip = request.form["ip"]

    post_object = {
        'node_address': "http://"+ip+":8000",
    }

    # Submit a transaction
    new_connection = "{}/register_with".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_connection,
                  json=post_object,
                  headers={'Content-type': 'application/json'})
    return redirect('/')

def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')

@app.route('/submit_last_block', methods=['POST'])
def submit_block():
    """
    Endpoint to send the last block mined to peers
    """

    for peer in peers:
        if peer == host_address:
            continue
        url = "http://{}:8000/add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(blocks[0], sort_keys=True),
                      headers=headers)

    return redirect('/')