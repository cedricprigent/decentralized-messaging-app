# decentralized-messaging-app

## Table of Contents
1. [General Info](#general-info)
2. [Requirements](#requirements)
3. [Execution](#execution)

## General Info

Application blockchain de messagerie décentralisée</br>
Il s'agit d'une version modifiée d'une application déjà existante.</br>
Lien vers l'application originale:
https://github.com/satwikkansal/python_blockchain_app

## Requirements

Installation des dépendances
```sh
$ pip install Flask
$ pip install requests
$ pip install socket
$ pip install hashlib
```

## Execution

Avant de lancer l'application
```sh
$ export FLASK_APP=node.py
```

Lancement de l'application grâce au script start_node.sh
```sh
$ ./start_node.sh
```

Lancement de l'application en exécutant les commandes suivantes dans 2 terminaux
```sh
$ flask run -h 'adresse réseau du noeud' --port 8000
$ python run_app.py
```
