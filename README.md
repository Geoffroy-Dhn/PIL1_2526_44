```markdown
# 🏫 IFRI_MentorLink

Application web de mise en relation mentor-mentoré pour les étudiants de l'IFRI.

---

## 📋 Table des matières

1. [Fonctionnalités](#-fonctionnalités)
2. [Technologies](#-technologies)
3. [Prérequis](#-prérequis)
4. [Installation Linux / macOS](#-installation-linux--macos)
5. [Installation Windows](#-installation-windows)
6. [Configuration](#-configuration)
7. [Démarrage](#-démarrage)
8. [Structure](#-structure)
9. [Dépannage](#-dépannage)

---

## ✨ Fonctionnalités

| Module | Description |
|--------|-------------|
| 🔐 Authentification | Inscription, connexion, réinitialisation mot de passe |
| 👤 Profil | Photo, bio, compétences, disponibilités |
| 📢 Offres/Demandes | Publication de mentorat par compétence |
| 🎯 Matching | Algorithme basé sur compétences, filière, niveau, disponibilités |
| 💬 Messagerie | Conversation en temps réel |
| 📊 Dashboard | Statistiques et résumé d'activité |

---

## 🛠 Technologies

| Technologie | Version **obligatoire** |
|-------------|--------------------------|
| Python | **3.13** (uniquement) |
| PostgreSQL | 15, 16 ou 17 |
| Flask | 2.3.3 |
| Flask-SocketIO | 5.3.4 |

> ⚠️ **Python 3.13 est imposé** pour garantir la compatibilité des dépendances.

---

## 📦 Prérequis

- Python 3.13
- PostgreSQL (15, 16 ou 17)
- pip (version récente)

---

## 🐧 Installation sur Linux / macOS

### 1. Installer Python 3.13

```bash
# Ubuntu/Debian
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-dev

# macOS
brew install python@3.13
```

### 2. Extraire le projet

```bash
cd ~/Documents
tar -xzf IFRI_MentorLink.tar.gz
cd IFRI_MentorLink
```

### 3. Créer l'environnement virtuel

```bash
python3.13 -m venv venv
source venv/bin/activate
```

### 4. Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configurer PostgreSQL

```bash
sudo systemctl start postgresql
sudo -u postgres psql -c "CREATE DATABASE mentorlink_db;"
sudo -u postgres psql -d mentorlink_db -f database/mentorlink_db.sql
```

### 6. Configurer l'application

```bash
nano backend/config.py
# Modifier DB_PASSWORD
```

### 7. Lancer

```bash
python3.13 run.py
```

---

## 🪟 Installation sur Windows

### 1. Installer Python 3.13

- Télécharger sur [python.org/downloads](https://www.python.org/downloads/)
- **Version 3.13.x** (64-bit)
- ✅ **Cocher "Add Python to PATH"**
- ✅ **Cocher "Install for all users"**

### 2. Extraire le projet

Extraire l'archive ZIP dans `C:\IFRI_MentorLink` (éviter les espaces dans le chemin)

### 3. Créer l'environnement virtuel

```cmd
cd C:\IFRI_MentorLink
py -3.13 -m venv venv
```

### 4. Activer l'environnement virtuel

```cmd
venv\Scripts\activate.bat
```

> ⚠️ **Si PowerShell bloque l'exécution :**

```powershell
# Ouvrir PowerShell en administrateur
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Puis réessayer :
venv\Scripts\Activate.ps1
```

> ⚠️ **Si vous utilisez Git Bash :**

```bash
source venv/Scripts/activate
```

### 5. Installer les dépendances

```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> ⚠️ **Si erreur avec psycopg2-binary :**

```cmd
pip install psycopg2-binary==2.9.9 --no-cache-dir
```

### 6. Installer PostgreSQL sur Windows

- Télécharger [postgresql.org/download/windows/](https://www.postgresql.org/download/windows/)
- Version : **16** ou **17**
- **Noter impérativement le mot de passe** choisi
- ✅ Cocher "Command Line Tools"

### 7. Ajouter PostgreSQL au PATH

1. Panneau de configuration → Variables d'environnement
2. Ajouter `C:\Program Files\PostgreSQL\16\bin`
3. Redémarrer l'invite de commande

### 8. Créer la base de données

**Méthode 1 (ligne de commande) :**
```cmd
psql -U postgres -c "CREATE DATABASE mentorlink_db;"
psql -U postgres -d mentorlink_db -f database\mentorlink_db.sql
```

**Méthode 2 (pgAdmin - recommandé débutant) :**
1. Ouvrir pgAdmin
2. Créer base `mentorlink_db` (Encoding: UTF8, Template: template0)
3. Clic droit → Query Tool
4. Ouvrir `database\mentorlink_db.sql` → Exécuter (F5)

### 9. Configurer l'application

Ouvrir `backend\config.py` avec le Bloc-notes :

```python
DB_PASSWORD = 'le_mot_de_passe_que_vous_avez_choisi'
```

### 10. Lancer l'application

```cmd
python run.py
```

### 11. Accéder à l'application

Ouvrir `http://127.0.0.1:5000` dans le navigateur

---

## ⚙ Configuration

### Fichier `backend/config.py`

```python
class Config:
    # PostgreSQL (À MODIFIER)
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    DB_NAME = 'mentorlink_db'
    DB_USER = 'postgres'
    DB_PASSWORD = 'admin123'  # ← METTRE VOTRE MOT DE PASSE
    
    # Sécurité (NE PAS MODIFIER EN PRODUCTION)
    SECRET_KEY = 'ta-cle-secrete-tres-longue-2026'
    JWT_SECRET_KEY = 'jwt-cle-secrete-2026'
```

### Réinitialiser la base (repartir de zéro)

**Linux/macOS :**
```bash
sudo -u postgres psql -c "DROP DATABASE IF EXISTS mentorlink_db; CREATE DATABASE mentorlink_db;"
sudo -u postgres psql -d mentorlink_db -f database/mentorlink_db.sql
```

**Windows :**
```cmd
psql -U postgres -c "DROP DATABASE IF EXISTS mentorlink_db; CREATE DATABASE mentorlink_db;"
psql -U postgres -d mentorlink_db -f database\mentorlink_db.sql
```

---

## 🚀 Démarrage rapide

### Linux / macOS

```bash
cd ~/Documents/IFRI_MentorLink
source venv/bin/activate
python3.13 run.py
```

### Windows

```cmd
cd C:\IFRI_MentorLink
venv\Scripts\activate
python run.py
```

### Accès

| Page | URL |
|------|-----|
| Connexion / Inscription | `http://127.0.0.1:5000/login.html` |
| Tableau de bord | `http://127.0.0.1:5000/dashboard.html` |
| API Health | `http://127.0.0.1:5000/api/health` |

---

## 📁 Structure

```
IFRI_MentorLink/
├── backend/
│   ├── app.py                 # Application Flask
│   ├── config.py              # Configuration
│   ├── models/user.py         # Modèle utilisateur
│   ├── routes/auth.py         # Routes authentification
│   └── services/              # Services (matching...)
├── frontend/
│   ├── *.html                 # Pages HTML
│   ├── css/                   # Styles
│   └── js/                    # Scripts
├── database/
│   └── mentorlink_db.sql      # Initialisation BDD
├── requirements.txt
├── run.py
└── README.md
```

---

## 🔧 Dépannage

### Problème : `psycopg2-binary` ne s'installe pas

```cmd
pip install psycopg2-binary==2.9.9 --no-cache-dir
```

### Problème : `ModuleNotFoundError: No module named 'backend'`

Assurez-vous d'être dans le dossier racine du projet.

### Problème : Connexion PostgreSQL échoue

1. Vérifier que PostgreSQL est démarré
2. Vérifier le mot de passe dans `config.py`
3. Tester la connexion :
   ```cmd
   psql -U postgres -c "SELECT 1"
   ```

### Problème : Port 5000 déjà utilisé

Modifier `run.py` :
```python
socketio.run(app, host='0.0.0.0', port=5001, debug=True)
```

### Problème : PowerShell bloque l'exécution des scripts

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problème : Erreur d'encodage UTF-8 sur Windows

Dans pgAdmin, lors de la création de la base :
- Encoding : `UTF8`
- Template : `template0`

### Problème : Aucun match n'apparaît

1. Aller dans **Mon profil** → Ajouter points forts et lacunes
2. Aller dans **Offres/Demandes** → Publier offres et demandes
3. Aller dans **Matching** → Cliquer "Générer de nouveaux matches"

---

## 👥 Auteurs

**Groupe PIL1_2526_44 - IFRI / Université d'Abomey-Calavi**
--DJEHONNON Geoffroy
--BEHANZIN Godwin
--DEGBELO Adler
--AZIGUITA Augustin
--SIDI Anas
--AÏZANNON Marjurès
--da SILVA Chimed

### Encadrement
- M. Ratheil HOUNDJI (Supervision)
- M. Armand ACCROMBESSI
- Mme Maryse GAHOU

---

## 📄 Licence

Projet réalisé dans le cadre de l'unité d'enseignement "Projet intégrateur".
```
