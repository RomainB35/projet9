# 🚀 Projet 9 — Déploiement d'un modèle de transcription audio

Ce répertoire contient le code pour créer deux images docker qui servent à mettre en oeuvre un service de transcription audio vers texte :

- **FastAPI** : expose une API qui sert un modèle **faster-whisper distilled (français)**.  
- **Streamlit** : fournit une interface web de démonstration pour interagir avec le modèle.  

---

## 📂 Structure du projet

```
projet9/
├── fastapi/       # API backend (serveur FastAPI)
│   ├── Dockerfile
│   ├── app/app.py
│   ├── download_model.py   # script pour télécharger le modèle avant build
│   └── requirements.txt
│
└── streamlit/    # Frontend (application Streamlit)
    ├── Dockerfile
    ├── requirements.txt
    └── app/
        ├── app.py
        ├── transcripts.json
        └── samples/
            ├── ...

```


---

## ⚙️ Prérequis

- Docker installé ([guide officiel](https://docs.docker.com/get-docker/)).  
- Connexion Internet (le script `download_model.py` télécharge le modèle avant la construction de l’image FastAPI).  
- (Optionnel) `python`/venv pour exécuter `download_model.py` localement si tu veux pré-télécharger le modèle hors du conteneur.

---

## 🛠️ Construction des images Docker

> **Important :** dans `fastapi/`, il faut d’abord télécharger le modèle avec `download_model.py` avant de construire l'image.

### 1. Préparer et construire l’image **FastAPI**

```bash
cd fastapi


# Télécharger le modèle (le script doit être présent dans fastapi/download_model.py)
python download_model.py

# Construire l’image Docker (le modèle téléchargé sera inclus si le Dockerfile copie les fichiers nécessaires)
docker build -t projet9-fastapi .
```

### 2. Construire l’image **Streamlit**

```bash
cd ../streamlit

docker build -t projet9-streamlit .
```

---

## ▶️ Lancer les conteneurs

### 0. Créer un réseau docker pour connecter les containers Fastapi et Streamlit

```bash
docker network create webnet
```

### 1. Lancer FastAPI

```bash
docker run -d \
  --name projet9-fastapi \
  --network webnet \
  -p 10300:10300 \
  projet9-fastapi
```

L’API sera accessible sur :  
👉 `http://localhost:10300/docs` (Swagger UI si Uvicorn/FastAPI exposent `/docs`)

---

### 2. Lancer Streamlit

```bash
docker run -d \
  --name projet9-streamlit \
  --network webnet \
  -p 8501:8501 \
  projet9-streamlit
```

L’application sera accessible sur :  
👉 `http://localhost:8501`


---

## 🧹 Gestion des conteneurs

Arrêter les conteneurs :

```bash
docker stop projet9-fastapi projet9-streamlit
```

Supprimer les conteneurs :

```bash
docker rm projet9-fastapi projet9-streamlit
```


---

## ✅ Résumé rapide (workflow)

1. Se placer dans `fastapi/` et lancer le téléchargement du modèle :  
   `python download_model.py`  
2. Construire l’image FastAPI :  
   `docker build -t projet9-fastapi .`  
3. Construire l’image Streamlit depuis `streamlit/` :  
   `docker build -t projet9-streamlit .`  
4. Lancer les conteneurs :  
   - `docker run -d --name projet9-fastapi -p 10300:10300 projet9-fastapi`  
   - `docker run -d --name projet9-streamlit -p 8501:8501 projet9-streamlit`  
5. Visiter :  
   - API : `http://localhost:10300/docs`  
   - UI : `http://localhost:8501`

---
