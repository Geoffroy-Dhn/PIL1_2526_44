# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, current_app
from backend.models.user import User
import re
import traceback

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^[0-9]{8,15}$'
    return re.match(pattern, phone) is not None

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json(force=True, silent=True)
        
        # Validation
        if not data.get('nom') or not data.get('prenom'):
            return jsonify({'error': 'Nom et prenom requis'}), 400
        
        if not data.get('email') or not validate_email(data['email']):
            return jsonify({'error': 'Email invalide'}), 400
        
        if not data.get('telephone') or not validate_phone(data['telephone']):
            return jsonify({'error': 'Telephone invalide (8-15 chiffres)'}), 400
        
        if not data.get('mot_de_passe') or len(data['mot_de_passe']) < 6:
            return jsonify({'error': 'Mot de passe doit faire au moins 6 caractères'}), 400
        
        if not data.get('id_filiere'):
            return jsonify({'error': 'Filière requise'}), 400
        
        db = current_app.config['get_db']()
        user = User(db)
        
        # Verifier si l'email existe dejà
        existing = user.find_by_email(data['email'])
        if existing:
            return jsonify({'error': 'Email dejà utilise'}), 409
        
        # role est fixe à 'les_deux' par defaut (l'utilisateur peut être mentor ET mentore)
        user_id = user.create(data)
        token = user.generate_token(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Inscription reussie',
            'token': token,
            'user_id': user_id
        }), 201
    except Exception as e:
        print("Erreur inscription:", str(e))
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json(force=True, silent=True)
        if not data.get('email') or not data.get('mot_de_passe'):
            return jsonify({'error': 'Email et mot de passe requis'}), 400
        
        db = current_app.config['get_db']()
        user = User(db)
        
        user_data = user.find_by_email(data['email'])
        if not user_data:
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        
        hashed_password = user_data['mot_de_passe']
        user_id = user_data['id_utilisateur']
        
        if not user.verify_password(data['mot_de_passe'], hashed_password):
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        
        token = user.generate_token(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Connexion reussie',
            'token': token,
            'user_id': user_id,
            'user': {
                'id': user_data['id_utilisateur'],
                'nom': user_data['nom'],
                'prenom': user_data['prenom'],
                'email': user_data['email'],
                'telephone': user_data['telephone']
            }
        })
    except Exception as e:
        print("Erreur connexion:", str(e))
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify', methods=['GET'])
def verify():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'valid': False, 'error': 'Token manquant'}), 401
        
        db = current_app.config['get_db']()
        user = User(db)
        user_id = user.verify_token(token)
        
        if not user_id:
            return jsonify({'valid': False, 'error': 'Token invalide'}), 401
        
        user_data = user.find_by_id(user_id)
        if not user_data:
            return jsonify({'valid': False, 'error': 'Utilisateur non trouve'}), 401
        
        return jsonify({
            'valid': True,
            'user_id': user_id,
            'user': {
                'id': user_data['id_utilisateur'],
                'nom': user_data['nom'],
                'prenom': user_data['prenom'],
                'email': user_data['email']
            }
        })
    except Exception as e:
        print("Erreur verify:", str(e))
        return jsonify({'valid': False, 'error': str(e)}), 401
# ==================== ROUTES PASSWORD RESET ====================

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email requis'}), 400
    
    db = current_app.config['get_db']()
    cursor = db.cursor()
    cursor.execute("SELECT id_utilisateur FROM utilisateur WHERE email = %s", (email,))
    user = cursor.fetchone()
    
    if not user:
        # Pour des raisons de securite, on ne revèle pas que l'email n'existe pas
        return jsonify({'success': True, 'message': 'Si cet email existe, un lien de reinitialisation vous a ete envoye'})
    
    # Generer un token unique
    import secrets
    reset_token = secrets.token_urlsafe(32)
    
    # Expiration dans 1 heure
    from datetime import datetime, timedelta
    expires = datetime.utcnow() + timedelta(hours=1)
    
    cursor.execute("""
        UPDATE utilisateur 
        SET reset_token = %s, reset_token_expiration = %s
        WHERE id_utilisateur = %s
    """, (reset_token, expires, user['id_utilisateur']))
    db.commit()
    cursor.close()
    
    # En developpement, on retourne le lien directement
    reset_link = f"http://127.0.0.1:5000/reset-password.html?token={reset_token}"
    
    return jsonify({
        'success': True, 
        'message': 'Un lien de reinitialisation a ete genere',
        'reset_link': reset_link
    })

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    
    if not token or not new_password or len(new_password) < 6:
        return jsonify({'error': 'Token invalide ou mot de passe trop court (min 6 caractères)'}), 400
    
    db = current_app.config['get_db']()
    cursor = db.cursor()
    
    from datetime import datetime
    cursor.execute("""
        SELECT id_utilisateur FROM utilisateur 
        WHERE reset_token = %s AND reset_token_expiration > %s
    """, (token, datetime.utcnow()))
    user = cursor.fetchone()
    
    if not user:
        return jsonify({'error': 'Lien invalide ou expire'}), 400
    
    # Hasher le nouveau mot de passe
    import bcrypt
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    cursor.execute("""
        UPDATE utilisateur 
        SET mot_de_passe = %s, reset_token = NULL, reset_token_expiration = NULL
        WHERE id_utilisateur = %s
    """, (hashed_password, user['id_utilisateur']))
    db.commit()
    cursor.close()
    
    return jsonify({'success': True, 'message': 'Mot de passe modifie avec succès'})

@auth_bp.route('/verify-reset-token', methods=['GET'])
def verify_reset_token():
    token = request.args.get('token')
    
    if not token:
        return jsonify({'valid': False, 'error': 'Token manquant'}), 400
    
    db = current_app.config['get_db']()
    cursor = db.cursor()
    
    from datetime import datetime
    cursor.execute("""
        SELECT id_utilisateur FROM utilisateur 
        WHERE reset_token = %s AND reset_token_expiration > %s
    """, (token, datetime.utcnow()))
    user = cursor.fetchone()
    cursor.close()
    
    if not user:
        return jsonify({'valid': False, 'error': 'Lien invalide ou expire'}), 400
    
    return jsonify({'valid': True})
