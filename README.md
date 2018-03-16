# La BlockChain pour les dev
Exemple de fonctionnement d'une blockchain extrêmement basique à des fins purement pédagogiques.

# Prérequis
python 3.6+

# Installation

```
> pip install -r requirements.txt
```

# Lancement

```
> python api.py
```

# Fonctionnement

## Affiche la chaine

```
curl --request GET --url http://localhost:5000/chain
```

## Crée une transaction

```
curl --request POST \
  --url http://localhost:5000/transactions \
  --header 'content-type: application/json' \
  --data '{
	"sender":"d4ee26eee15148ee92c6cd394edd974e",
	"recipient":"toi",
	"amount":10
}'
```

## Mine

```
curl --request POST --url http://localhost:5000/blocks
```
