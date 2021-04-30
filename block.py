from hashlib import sha256
import json
import time

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        """
        Constructeur pour la classe "Block"
        @param index: ID unique
        @param transactions: Les transactions contenues dans le block
        @param timestamp: Date de génération du block 
        @param previous_hash: Hash du block précédent
        """

        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = None

    def compute_hash(self):
        """
        Calcule le hash du block en convertissant le block en chaîne JSON
        puis en convertissant la chaîne obtenue avec fonction de hash SHA256
        """

        block_string = json.dumps(self.__dict__, sort_keys = True)
        return sha256(block_string.encode()).hexdigest()

        