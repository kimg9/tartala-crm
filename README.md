# 📘 README – TartalaCRM

## 🎯 Contexte

Ce projet implémente un **CRM en Python (CLI)** permettant de gérer **clients, contrats et événements**, avec gestion des rôles (gestion, commerciaux, support) et une sécurité renforcée.

L’architecture suit un modèle **Domain / Repository** afin de séparer clairement :

* la **logique métier** (domain)
* la **persistance des données** (repositories avec SQLAlchemy)
* la **configuration DB**
* les **modèles** (mapping objet-relationnel)


## 🛠️ Technologies utilisées

* **Langage** : Python 3.9+
* **ORM** : SQLAlchemy
* **Base de données** : (PostgreSQL/MySQL/SQLite selon l’environnement)
* **CLI** : Application en ligne de commande
* **Journalisation** : Sentry


## 📂 Structure du projet

```
├── db_config/          # Configuration de la base de données
│   ├── base.py         # Base declarative SQLAlchemy
│   ├── connexion.py    # Connexion DB
│   └── __init__.py
│
├── domain/             # Logique métier (use cases / services)
│   ├── client_app.py   # Cas d’usage liés aux clients
│   ├── contract_app.py # Cas d’usage liés aux contrats
│   ├── event_app.py    # Cas d’usage liés aux événements
│   └── user_app.py     # Cas d’usage liés aux utilisateurs
│
├── models/             # Définition des entités ORM
│   └── models.py
│
├── repositories/       # Accès aux données (pattern Repository)
│   ├── clients/        # Repo pour Client
│   ├── contracts/      # Repo pour Contract
│   ├── events/         # Repo pour Event
│   └── users/          # Repo pour User
│
├── tartala-crm/        # CLI principale
│
├── utils.py            # Fonctions utilitaires
├── requirements.txt    # Dépendances
└── README.md
```

## ⚙️ Configuration

Créer un fichier `.envrc` avec vos variables :

```ini
export DATABASE_URL=postgresql://user:password@localhost:5432/epic_events
export SENTRY_DSN=<votre_dsn_sentry>
export JWT_SECRET=<votre_secret_jwt>
```


## 📦 Installation

```bash
# Créer un venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt
```


## ▶️ Utilisation

### Commandes disponibles

#### 🔍 Lister des éléments

```bash
python tartala-crm.py list_items clients
python tartala-crm.py list_items events
python tartala-crm.py list_items contracts
```

#### ➕ Créer un élément

```bash
python tartala-crm.py create_item client
python tartala-crm.py create_item event
python tartala-crm.py create_item contract
python tartala-crm.py create_item user
```

#### ✏️ Mettre à jour un élément

```bash
python tartala-crm.py update_item client 1 #Le numéro correspond à l'id de la ressource à mettre à jour
python tartala-crm.py update_item event 2
python tartala-crm.py update_item contract 3
python tartala-crm.py update_item user 4
```

#### 🗑️ Supprimer un élément

```bash
python tartala-crm.py delete_item client 1
python tartala-crm.py delete_item event 2
python tartala-crm.py delete_item contract 3
python tartala-crm.py delete_item user 4
```

⚠️ L’utilisateur doit être **authentifié** avant d’exécuter des actions.
Pour s'authentifier, utiliser la commande :
```bash
python tartala-crm.py login
```


## 👥 Rôles et permissions

* **Équipe gestion** : gestion des utilisateurs, modification globale des contrats/événements.
* **Équipe commerciale** : création/édition de leurs clients, contrats et événements.
* **Équipe support** : gestion des événements assignés.
* **Tous** : lecture globale.


## 🚀 Fonctionnalités

* Authentification par identifiants
* Sécurité via **principe du moindre privilège**
* Gestion **clients / contrats / événements**
* Requêtes sécurisées (SQLAlchemy)
* Journalisation des erreurs avec **Sentry**
* Filtres dynamiques (contrats non signés, événements sans support, etc.)
