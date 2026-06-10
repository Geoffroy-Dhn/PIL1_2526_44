# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, current_app
from backend.models.user import User

offres_bp = Blueprint('offres', __name__, url_prefix='/api')

@offres_bp.route('/offres/publier', methods=['POST'])
def publier_offre():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = User(current_app.config['get_db']())
    user_id = user.verify_token(token)
    
    if not user_id:
        return jsonify({'error': 'Non autorisé'}), 401
    
    data = request.get_json()
    titre = data.get('titre')
    id_competence = data.get('id_competence')
    description = data.get('description', '')
    format_session = data.get('format_session', 'les_deux')
    disponibilites = data.get('disponibilites', [])
    
    if not titre or not id_competence:
        return jsonify({'error': 'Titre et compétence requis'}), 400
    
    db = current_app.config['get_db']()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            SELECT 1 FROM profil_competence 
            WHERE id_utilisateur = %s AND id_competence = %s AND type_maitrise = 'fort'
        """, (user_id, id_competence))
        if not cursor.fetchone():
            return jsonify({'error': 'Vous ne pouvez proposer du mentorat que dans vos points forts'}), 403
        
        import json
        cursor.execute("""
            INSERT INTO offre_mentorat (id_utilisateur, titre, description, format_session, disponibilites, statut)
            VALUES (%s, %s, %s, %s, %s, 'active')
            RETURNING id_offre
        """, (user_id, titre, description, format_session, json.dumps(disponibilites)))
        offre_id = cursor.fetchone()['id_offre']
        
        cursor.execute("""
            INSERT INTO offre_competence (id_offre, id_competence)
            VALUES (%s, %s)
        """, (offre_id, id_competence))
        
        db.commit()
        return jsonify({'success': True, 'message': 'Offre publiée', 'offre_id': offre_id}), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@offres_bp.route('/demandes/publier', methods=['POST'])
def publier_demande():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = User(current_app.config['get_db']())
    user_id = user.verify_token(token)
    
    if not user_id:
        return jsonify({'error': 'Non autorisé'}), 401
    
    data = request.get_json()
    titre = data.get('titre')
    id_competence = data.get('id_competence')
    description = data.get('description', '')
    format_session = data.get('format_session', 'les_deux')
    disponibilites = data.get('disponibilites', [])
    
    if not titre or not id_competence:
        return jsonify({'error': 'Titre et compétence requis'}), 400
    
    db = current_app.config['get_db']()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            SELECT 1 FROM profil_competence 
            WHERE id_utilisateur = %s AND id_competence = %s AND type_maitrise = 'faible'
        """, (user_id, id_competence))
        if not cursor.fetchone():
            return jsonify({'error': 'Vous ne pouvez demander du mentorat que pour vos lacunes'}), 403
        
        import json
        cursor.execute("""
            INSERT INTO demande_mentorat (id_utilisateur, titre, description, format_session, disponibilites, statut)
            VALUES (%s, %s, %s, %s, %s, 'active')
            RETURNING id_demande
        """, (user_id, titre, description, format_session, json.dumps(disponibilites)))
        demande_id = cursor.fetchone()['id_demande']
        
        cursor.execute("""
            INSERT INTO demande_competence (id_demande, id_competence)
            VALUES (%s, %s)
        """, (demande_id, id_competence))
        
        db.commit()
        return jsonify({'success': True, 'message': 'Demande publiée', 'demande_id': demande_id}), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
