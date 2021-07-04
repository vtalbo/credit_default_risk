# Prêt à dépenser - Prédiction du défaut de paiement
A partir des données d'un projet kaggle : https://www.kaggle.com/c/home-credit-default-risk/

Les objectifs sont de: 
- Développer un modèle de scoring de la probabilité de défaut de paiement du client
- Avoir à disposition un dashboard interactif permettant de comprendre la décision aux commerciaux et aux clients

Le dossier se compose ainsi :
- La méthodologie de traitement des données, obtention du modèle, et tests liés au déploiement du dashboard sont dans
le dossier `notebooks` 
- L'application Flask permettant de déployer le dashboard et l'API de prédiction du score se trouvent dans le dossier 
`app` 
- Les librairies nécessaires au bon déploiement des applications sont dans le fichier `requirements.txt`
  
Ce github est suivi en direct par heroku pour un déploiement instantané sur 
- https://home-credit-default.herokuapp.com/ pour le dashboard
- https://home-credit-default.herokuapp.com/test_credit pour la prédiction de défaut de paiement


Pour le deployer en local, utilisez la commande :
`gunicorn wsgi:app `