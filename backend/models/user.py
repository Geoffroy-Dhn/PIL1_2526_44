from datetime import datetime, timedelta
import bcrypt
import jwt
from flask import current_app

class User:
    def __init__(self, db):
        self.db = db
    
    def create(self, data):
        query = """
            INSERT INTO utilisateur (nom, prenom, email, telephone, mot_de_passe, id_filiere, niveau_etudes, role, photo_profil, bio)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_utilisateur
        """
        hashed_password = bcrypt.hashpw(data['mot_de_passe'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        role = data.get('role', 'les_deux')
        niveau = data.get('niveau_etudes', 'L1')
        photo = data.get('photo_profil', '')
        bio = data.get('bio', '')
        
        cursor = self.db.cursor()
        cursor.execute(query, (
            data['nom'], data['prenom'], data['email'], data['telephone'],
            hashed_password, int(data['id_filiere']), niveau, role, photo, bio
        ))
        
        result = cursor.fetchone()
        user_id = result['id_utilisateur'] if isinstance(result, dict) else result[0]
        
        self.db.commit()
        cursor.close()
        return user_id
    
    def update(self, user_id, data):
        query = """
            UPDATE utilisateur 
            SET nom = %s, prenom = %s, telephone = %s, 
                photo_profil = %s, bio = %s, niveau_etudes = %s, id_filiere = %s,
                date_modification = CURRENT_TIMESTAMP
            WHERE id_utilisateur = %s
            RETURNING id_utilisateur
        """
        cursor = self.db.cursor()
        cursor.execute(query, (
            data['nom'], data['prenom'], data['telephone'],
            data.get('photo_profil', ''), data.get('bio', ''),
            data.get('niveau_etudes', 'L1'), int(data['id_filiere']),
            user_id
        ))
        self.db.commit()
        cursor.close()
        return user_id
    
    def find_by_email(self, email):
        query = "SELECT * FROM utilisateur WHERE email = %s"
        cursor = self.db.cursor()
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        cursor.close()
        return user
    
    def find_by_id(self, user_id):
        query = "SELECT * FROM utilisateur WHERE id_utilisateur = %s"
        cursor = self.db.cursor()
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        cursor.close()
        return user
    
    def verify_password(self, password, hashed):
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_token(self, user_id):
        expiration = datetime.utcnow() + timedelta(hours=24)
        payload = {'user_id': user_id, 'exp': expiration}
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    def verify_token(self, token):
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return payload['user_id']
        except:
            return None
