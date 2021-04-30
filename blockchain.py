from hashlib import sha256
import json
import time

from block import Block
from exceptions import *

class Blockchain:
    def __init__(self, genesis_block=None):
        """
        Constructeur pour la classe "Blockchain"
        """
        self.unconfirmed_transactions = []
        self.chain = []

        if genesis_block == None:
            self.create_genesis_block()
        else:
            self.chain.append(genesis_block)

        self.difficulty = 3

    @property
    def last_block(self):
        """
        Retourne le dernier "Block" de la chaîne
        """
        return self.chain[-1]

    def __str__(self):
        """
        Retourne une chaîne de caractères représentant la "Blockchain"
        """
        str_repr = "Blockchain object\n{"
        for block in self.chain:
            str_repr += "Block object "
            str_repr += str(block.__dict__)
            if block.compute_hash() == self.last_block.compute_hash():
                str_repr += "}"
            else:
                str_repr += ",\n"
        return str_repr

    def create_genesis_block(self):
        """
        Génère le "Block" genesis de la "Blockchain"
        """
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    def add_block(self, block, proof):
        """
        Ajoute un "Block" à la chaîne après une vérification
        La vérification inclue:
        * Vérfication de la validité de la preuve
        * Le previous_hash spécifié dans le "Block" et le hash du dernier block de la chaîne correspondent
        """ 
        #previous_hash = self.last_block.hash

        try:
            if self.last_block.hash != block.previous_hash:
                raise InvalidHashError()
            if not self.is_valid_proof(block, proof):
                raise InvalidProofError()
            block.hash = proof
            self.chain.append(block)
            return True
        except InvalidHashError:
            print("Exception: Le previous_hash du nouveau Block et le hash du last_block de la chaîne ne correspondent pas\n")
            print("previous_hash : \t" + block.previous_hash +"\n")
            print("last block hash : \t" + self.last_block.hash +"\n")
            return False
        except InvalidProofError:
            print("Exception: La preuve de travail est invalide")
            return False

    def proof_of_work(self, block):
        """
        Essaie différentes valeur pour le nonce de façon à trouver un hash qui satisfait le niveau de difficulté choisi
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def is_valid_proof(self, block, block_hash):
        """
        Vérifie si le block_hash correspond au hash du block et si cela satisfait le niveau de difficulté
        """
        return (block_hash.startswith('0' * self.difficulty) and
                block_hash == block.compute_hash())

    def add_new_transaction(self, transaction):
        """
        Ajoute une transaction au "Block" en cours de minage
        """
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        """
        Ajoute les transactions en attente à la "Blockchain"
        Calcul la preuve de travail
        """
        try:
            if not self.unconfirmed_transactions:
                raise NoTransactionsError()
        except NoTransactionsError:
                print("Exception: Aucune transaction en attente")
                return False

        last_block = self.last_block

        new_block = Block(index = last_block.index + 1,
                          transactions = self.unconfirmed_transactions,
                          timestamp = time.time(),
                          previous_hash = last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        return new_block.index


    def check_chain_validity(cls, chain):
        """
        A helper method to check if the entire blockchain is valid.            
        """
        result = True
        previous_hash = "0"

        # Iterate through every block
        for block in chain:
            block_hash = block.hash
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block.hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result