# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
from backend.config import config
from backend.routes.auth import auth_bp
import psycopg2
from psycopg2.extras import RealDictCursor

socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY
    
    # CORS etendu pour autoriser toutes les origines (mode developpement)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    
    def get_db():
        conn = psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            cursor_factory=RealDictCursor
        )
        conn.set_client_encoding('UTF8')
        return conn
    
    app.config['get_db'] = get_db
    app.register_blueprint(auth_bp)
    @app.before_request
    def force_utf8():
        print(request)
        if request.mimetype == 'application/json':
            request.charset = 'utf-8'
    # ==================== ROUTES DE BASE ====================
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'ok', 'message': 'IFRI_MentorLink API running'})
    
    @app.route('/api/filieres', methods=['GET'])
    def get_filieres():
        db = app.config['get_db']()
        cursor = db.cursor()
        cursor.execute("SELECT id_filiere, code_filiere, libelle FROM filiere ORDER BY code_filiere")
        filieres = cursor.fetchall()
        cursor.close()
        return jsonify(filieres)
    
    @app.route('/api/competences', methods=['GET'])
    def get_all_competences():
        db = app.config['get_db']()
        cursor = db.cursor()
        cursor.execute("SELECT id_competence, nom, categorie FROM competence ORDER BY nom")
        competences = cursor.fetchall()
        cursor.close()
        return jsonify(competences)
    
    # ==================== ROUTES COMPETENCES ====================
    @app.route('/api/user/competences/<type_maitrise>', methods=['GET'])
    def get_user_competences(type_maitrise):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
        db = app.config['get_db']()
        cursor = db.cursor()
        cursor.execute("""
            SELECT c.id_competence, c.nom as nom_competence, c.categorie
            FROM profil_competence pc
            JOIN competence c ON pc.id_competence = c.id_competence
            WHERE pc.id_utilisateur = %s AND pc.type_maitrise = %s
        """, (user_id, type_maitrise))
        competences = cursor.fetchall()
        cursor.close()
        return jsonify(competences)
    
    @app.route('/api/user/competences', methods=['POST'])
    def add_user_competence():
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
        data = request.get_json()
        id_competence = data.get('id_competence')
        type_maitrise = data.get('type_maitrise')
        if not id_competence or type_maitrise not in ['fort', 'faible']:
            return jsonify({'error': 'Donnees invalides'}), 400
        db = app.config['get_db']()
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO profil_competence (id_utilisateur, id_competence, type_maitrise)
                VALUES (%s, %s, %s)
                ON CONFLICT (id_utilisateur, id_competence) 
                DO UPDATE SET type_maitrise = EXCLUDED.type_maitrise
            """, (user_id, id_competence, type_maitrise))
            # Supprimer les anciens matches
            cursor.execute("DELETE FROM matching WHERE id_mentor = %s OR id_mentore = %s", (user_id, user_id))
            db.commit()
            return jsonify({'success': True, 'message': 'Competence ajoutee'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
    
    @app.route('/api/user/competences/<int:competence_id>/<string:type_maitrise>', methods=['DELETE'])
    def delete_competence(competence_id, type_maitrise):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
        if type_maitrise not in ['fort', 'faible']:
            return jsonify({'error': 'Type invalide'}), 400
        db = app.config['get_db']()
        cursor = db.cursor()
        cursor.execute("DELETE FROM profil_competence WHERE id_utilisateur = %s AND id_competence = %s AND type_maitrise = %s", (user_id, competence_id, type_maitrise))
        db.commit()
        cursor.close()
        return jsonify({'success': True, 'message': 'Competence supprimee'})
    
    # ==================== ROUTES OFFRES ET DEMANDES ====================
    @app.route('/api/offres/publier', methods=['POST'])
    def publier_offre():
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
            
        # Dans app.py, au début de publier_offre :
        data = request.get_json()
        titre = data.get('titre')
        # On récupère une liste de compétences, pas juste une seule valeur
        liste_competences = data.get('competences', []) 
        description = data.get('description', '')
        format_session = data.get('format_session', 'les_deux')
        dispos = data.get('disponibilites', []) 

        if not titre or not liste_competences:
            return jsonify({'error': 'Titre et au moins une competence requis'}), 400
            
        db = app.config['get_db']()
        cursor = db.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO offre_mentorat (id_utilisateur, titre, description, format_session, statut) 
                VALUES (%s, %s, %s, %s, 'active') RETURNING id_offre
            """, (user_id, titre, description, format_session))
            
            result = cursor.fetchone()
            if not result:
                raise Exception("L'insertion dans offre_mentorat a échoué (aucun ID retourné).")
            
            # Utilisation de la clé si RealDictCursor est utilisé, ou index 0
            offre_id = result['id_offre'] if isinstance(result, dict) else result[0]
            
            # 2. Insertion des compétences
            for comp_id in liste_competences:
                cursor.execute("""
                    INSERT INTO offre_competence (id_offre, id_competence) 
                    VALUES (%s, %s)
                """, (offre_id, comp_id))
            
            # 3. Insertion des disponibilités dans la table dédiée
            for d in dispos:
                # Assurez-vous que les clés correspondent exactement à celles envoyées par le frontend
                cursor.execute("""
                    INSERT INTO offre_disponibilite (id_offre, jour_semaine, heure_debut, heure_fin) 
                    VALUES (%s, %s, %s, %s)
                """, (offre_id, d['jour'], d['debut'], d['fin']))
                
            db.commit()
            return jsonify({'success': True, 'message': 'Offre publiee', 'offre_id': offre_id}), 201
            
        except Exception as e:
            db.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
    
    @app.route('/api/demandes/publier', methods=['POST'])
    def publier_demande():
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
            
        data = request.get_json()
        titre = data.get('titre')
        # Harmonisation : on récupère la liste 'competences'
        liste_competences = data.get('competences', [])
        description = data.get('description', '')
        format_session = data.get('format_session', 'les_deux')
        dispos = data.get('disponibilites', [])

        if not titre or not liste_competences:
            return jsonify({'error': 'Titre et au moins une competence requis'}), 400
            
        db = app.config['get_db']()
        cursor = db.cursor()
        
        try:
            # 1. Insertion dans demande_mentorat
            cursor.execute("""
                INSERT INTO demande_mentorat (id_utilisateur, titre, description, format_session, statut) 
                VALUES (%s, %s, %s, %s, 'active') RETURNING id_demande
            """, (user_id, titre, description, format_session))
            
            demande_id = cursor.fetchone()['id_demande']
            
            # 2. Insertion des compétences associées
            for comp_id in liste_competences:
                cursor.execute("""
                    INSERT INTO demande_competence (id_demande, id_competence) 
                    VALUES (%s, %s)
                """, (demande_id, comp_id))
            
            # 3. Insertion des disponibilités
            for d in dispos:
                cursor.execute("""
                    INSERT INTO demande_disponibilite (id_demande, jour_semaine, heure_debut, heure_fin) 
                    VALUES (%s, %s, %s, %s)
                """, (demande_id, d['jour'], d['debut'], d['fin']))
                
            db.commit()
            return jsonify({'success': True, 'message': 'Demande publiee', 'demande_id': demande_id}), 201
            
        except Exception as e:
            db.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
    
    @app.route('/api/offres/mes-offres', methods=['GET'])
    def mes_offres():
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
        db = app.config['get_db']()
        cursor = db.cursor()
        cursor.execute("""
            SELECT o.*, c.nom as competence_nom
            FROM offre_mentorat o
            JOIN offre_competence oc ON o.id_offre = oc.id_offre
            JOIN competence c ON oc.id_competence = c.id_competence
            WHERE o.id_utilisateur = %s ORDER BY o.date_publication DESC
        """, (user_id,))
        offres = cursor.fetchall()
        cursor.close()
        return jsonify(offres)
    
    @app.route('/api/demandes/mes-demandes', methods=['GET'])
    def mes_demandes():
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
        db = app.config['get_db']()
        cursor = db.cursor()
        cursor.execute("""
            SELECT d.*, c.nom as competence_nom
            FROM demande_mentorat d
            JOIN demande_competence dc ON d.id_demande = dc.id_demande
            JOIN competence c ON dc.id_competence = c.id_competence
            WHERE d.id_utilisateur = %s ORDER BY d.date_publication DESC
        """, (user_id,))
        demandes = cursor.fetchall()
        cursor.close()
        return jsonify(demandes)
    
    # ==================== ROUTES MATCHING ====================
    @app.route('/api/matching/my-matches', methods=['GET'])
    def get_my_matches():
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
        db = app.config['get_db']()
        cursor = db.cursor()
        cursor.execute("""
            SELECT 
                m.id_matching, m.score_global,
                COALESCE(m.score_competences, 0) as score_competences,
                COALESCE(m.score_filiere, 0) as score_filiere,
                COALESCE(m.score_disponibilite, 0) as score_disponibilite,
                CASE WHEN m.id_mentor = %s THEN 'mentore' ELSE 'mentor' END as mon_role,
                CASE WHEN m.id_mentor = %s THEN u_autre.id_utilisateur ELSE u_autre.id_utilisateur END as id_autre,
                u_autre.nom, u_autre.prenom, u_autre.photo_profil
            FROM matching m
            JOIN utilisateur u_autre ON (CASE WHEN m.id_mentor = %s THEN m.id_mentore = u_autre.id_utilisateur ELSE m.id_mentor = u_autre.id_utilisateur END)
            WHERE (m.id_mentor = %s OR m.id_mentore = %s) AND m.statut = 'suggere'
            ORDER BY m.score_global DESC LIMIT 10
        """, (user_id, user_id, user_id, user_id, user_id))
        matches = cursor.fetchall()
        cursor.close()
        return jsonify(matches)
    
    @app.route('/api/matching/generate', methods=['POST'])
    def generate_matches():
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        from backend.services.matching_algorithm import MatchingAlgorithm
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
        db = app.config['get_db']()
        algo = MatchingAlgorithm(db)
        matches = algo.generate_matches_for_user(user_id)
        return jsonify({'success': True, 'message': f'{len(matches)} matches generes', 'matches_generes': len(matches)})
    
    @app.route('/api/matching/common-competences/<int:autre_id>', methods=['GET'])
    def get_common_competences(autre_id):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
        db = app.config['get_db']()
        cursor = db.cursor()
        cursor.execute("""
            SELECT DISTINCT c.id_competence, c.nom
            FROM profil_competence pc1
            JOIN profil_competence pc2 ON pc1.id_competence = pc2.id_competence
            JOIN competence c ON pc1.id_competence = c.id_competence
            WHERE ((pc1.id_utilisateur = %s AND pc1.type_maitrise = 'fort' AND pc2.id_utilisateur = %s AND pc2.type_maitrise = 'faible')
                OR (pc1.id_utilisateur = %s AND pc1.type_maitrise = 'faible' AND pc2.id_utilisateur = %s AND pc2.type_maitrise = 'fort'))
        """, (user_id, autre_id, user_id, autre_id))
        competences = cursor.fetchall()
        cursor.close()
        return jsonify(competences)
    
    @app.route('/api/matching/common-disponibilites/<int:autre_id>', methods=['GET'])
    def get_common_disponibilites(autre_id):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
        db = app.config['get_db']()
        cursor = db.cursor()
        cursor.execute("""
            SELECT d1.jour_semaine,
                   GREATEST(d1.heure_debut, d2.heure_debut) as heure_debut,
                   LEAST(d1.heure_fin, d2.heure_fin) as heure_fin
            FROM disponibilite d1
            JOIN disponibilite d2 ON d1.jour_semaine = d2.jour_semaine
                AND d1.heure_debut < d2.heure_fin AND d1.heure_fin > d2.heure_debut
            WHERE d1.id_utilisateur = %s AND d2.id_utilisateur = %s
        """, (user_id, autre_id))
        dispos = cursor.fetchall()
        cursor.close()
        for d in dispos:
            if d['heure_debut']:
                d['heure_debut'] = str(d['heure_debut'])[:5]
            if d['heure_fin']:
                d['heure_fin'] = str(d['heure_fin'])[:5]
        return jsonify(dispos)
    
    @app.route('/api/matching/clear', methods=['POST'])
    def clear_matches():
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
        db = app.config['get_db']()
        cursor = db.cursor()
        cursor.execute("DELETE FROM matching WHERE id_mentor = %s OR id_mentore = %s", (user_id, user_id))
        db.commit()
        cursor.close()
        return jsonify({'success': True, 'message': 'Matches supprimes'})
    
    @app.route('/api/matching/generate-all', methods=['POST'])
    def generate_all_matches():
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        from backend.services.matching_algorithm import MatchingAlgorithm
        
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
        
        db = app.config['get_db']()
        algo = MatchingAlgorithm(db)
        
        cursor = db.cursor()
        cursor.execute("SELECT id_utilisateur FROM utilisateur WHERE est_actif = TRUE")
        all_users = cursor.fetchall()
        cursor.close()
        
        total_matches = 0
        for u in all_users:
            uid = u['id_utilisateur']
            cursor = db.cursor()
            cursor.execute("DELETE FROM matching WHERE id_mentor = %s OR id_mentore = %s", (uid, uid))
            db.commit()
            cursor.close()
            matches = algo.generate_matches_for_user(uid)
            total_matches += len(matches)
        
        return jsonify({
            'success': True, 
            'message': f'{total_matches} matches generes pour tous les utilisateurs',
            'total_matches': total_matches
        })
    
    # ==================== ROUTES PROFIL ====================
    @app.route('/api/user/<int:user_id>', methods=['GET'])
    def get_user_profile(user_id):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        user = User(app.config['get_db']())
        auth_user_id = user.verify_token(token)
        if not auth_user_id:
            return jsonify({'error': 'Non autorise'}), 401
        db = app.config['get_db']()
        cursor = db.cursor()
        cursor.execute("""
            SELECT id_utilisateur, nom, prenom, email, telephone, 
                   COALESCE(photo_profil, '') as photo_profil, 
                   COALESCE(bio, 'Aucune information renseignee') as bio, 
                   niveau_etudes, id_filiere, role, date_inscription
            FROM utilisateur WHERE id_utilisateur = %s
        """, (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        if not user_data:
            return jsonify({'error': 'Utilisateur non trouve'}), 404
        return jsonify(user_data)
    
    @app.route('/api/user/update', methods=['PUT'])
    def update_user_profile():
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
        data = request.get_json()
        db = app.config['get_db']()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE utilisateur SET nom=%s, prenom=%s, telephone=%s, niveau_etudes=%s, id_filiere=%s, bio=%s, photo_profil=%s, date_modification=CURRENT_TIMESTAMP
            WHERE id_utilisateur=%s
        """, (data['nom'], data['prenom'], data['telephone'], data['niveau_etudes'], data['id_filiere'], data.get('bio', ''), data.get('photo_profil', ''), user_id))
        db.commit()
        cursor.close()
        return jsonify({'success': True, 'message': 'Profil mis à jour'})
    
    # ==================== ROUTES MESSAGERIE ====================
    @app.route('/api/conversations', methods=['GET'])
    def get_conversations():
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
        db = app.config['get_db']()
        cursor = db.cursor()
        cursor.execute("""
            SELECT c.id_conversation, c.date_dernier_msg,
                CASE WHEN c.id_utilisateur_1 = %s THEN u2.nom ELSE u1.nom END as autre_nom,
                CASE WHEN c.id_utilisateur_1 = %s THEN u2.prenom ELSE u1.prenom END as autre_prenom,
                CASE WHEN c.id_utilisateur_1 = %s THEN u2.photo_profil ELSE u1.photo_profil END as autre_photo,
                (SELECT contenu FROM message WHERE id_conversation = c.id_conversation ORDER BY date_envoi DESC LIMIT 1) as dernier_message,
                (SELECT COUNT(*) FROM message WHERE id_conversation = c.id_conversation AND est_lu = FALSE AND id_expediteur != %s) as non_lus
            FROM conversation c
            JOIN utilisateur u1 ON c.id_utilisateur_1 = u1.id_utilisateur
            JOIN utilisateur u2 ON c.id_utilisateur_2 = u2.id_utilisateur
            WHERE c.id_utilisateur_1 = %s OR c.id_utilisateur_2 = %s
            ORDER BY c.date_dernier_msg DESC
        """, (user_id, user_id, user_id, user_id, user_id, user_id))
        conversations = cursor.fetchall()
        cursor.close()
        return jsonify(conversations)
    
    @app.route('/api/conversations/<int:user_id_autre>', methods=['POST'])
    def create_or_get_conversation(user_id_autre):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
        db = app.config['get_db']()
        cursor = db.cursor()
        cursor.execute("SELECT id_conversation FROM conversation WHERE (id_utilisateur_1=%s AND id_utilisateur_2=%s) OR (id_utilisateur_1=%s AND id_utilisateur_2=%s)", (user_id, user_id_autre, user_id_autre, user_id))
        existing = cursor.fetchone()
        if existing:
            conv_id = existing['id_conversation']
        else:
            cursor.execute("INSERT INTO conversation (id_utilisateur_1, id_utilisateur_2) VALUES (%s, %s) RETURNING id_conversation", (user_id, user_id_autre))
            conv_id = cursor.fetchone()['id_conversation']
            db.commit()
        cursor.close()
        return jsonify({'conversation_id': conv_id})
    
    @app.route('/api/messages/<int:conversation_id>', methods=['GET'])
    def get_messages(conversation_id):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
        db = app.config['get_db']()
        cursor = db.cursor()
        cursor.execute("SELECT id_utilisateur_1, id_utilisateur_2 FROM conversation WHERE id_conversation = %s", (conversation_id,))
        conv = cursor.fetchone()
        if not conv or (conv['id_utilisateur_1'] != user_id and conv['id_utilisateur_2'] != user_id):
            return jsonify({'error': 'Non autorise'}), 403
        cursor.execute("UPDATE message SET est_lu = TRUE WHERE id_conversation = %s AND id_expediteur != %s", (conversation_id, user_id))
        cursor.execute("SELECT m.*, u.nom, u.prenom, u.photo_profil FROM message m JOIN utilisateur u ON m.id_expediteur = u.id_utilisateur WHERE m.id_conversation = %s ORDER BY m.date_envoi ASC", (conversation_id,))
        messages = cursor.fetchall()
        db.commit()
        cursor.close()
        return jsonify(messages)
    
    @app.route('/api/messages', methods=['POST'])
    def send_message():
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
        data = request.get_json()
        conversation_id = data.get('conversation_id')
        contenu = data.get('contenu', '').strip()
        if not conversation_id or not contenu:
            return jsonify({'error': 'Donnees invalides'}), 400
        db = app.config['get_db']()
        cursor = db.cursor()
        cursor.execute("SELECT id_utilisateur_1, id_utilisateur_2 FROM conversation WHERE id_conversation = %s", (conversation_id,))
        conv = cursor.fetchone()
        if not conv or (conv['id_utilisateur_1'] != user_id and conv['id_utilisateur_2'] != user_id):
            return jsonify({'error': 'Non autorise'}), 403
        cursor.execute("INSERT INTO message (id_conversation, id_expediteur, contenu) VALUES (%s, %s, %s) RETURNING id_message, date_envoi", (conversation_id, user_id, contenu))
        result = cursor.fetchone()
        cursor.execute("UPDATE conversation SET date_dernier_msg = CURRENT_TIMESTAMP WHERE id_conversation = %s", (conversation_id,))
        db.commit()
        cursor.close()
        return jsonify({'success': True, 'message_id': result['id_message'], 'date_envoi': result['date_envoi']})
    
    # ==================== ROUTES DISPONIBILITES ====================
    @app.route('/api/user/disponibilites', methods=['GET'])
    def get_disponibilites():
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
        db = app.config['get_db']()
        cursor = db.cursor()
        cursor.execute("SELECT id_disponibilite, jour_semaine, heure_debut, heure_fin FROM disponibilite WHERE id_utilisateur = %s", (user_id,))
        dispos = cursor.fetchall()
        cursor.close()
        for d in dispos:
            if d['heure_debut']:
                d['heure_debut'] = str(d['heure_debut'])[:5]
            if d['heure_fin']:
                d['heure_fin'] = str(d['heure_fin'])[:5]
        return jsonify(dispos)
    
    @app.route('/api/user/disponibilites', methods=['POST'])
    def add_disponibilite():
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
        data = request.get_json()
        db = app.config['get_db']()
        cursor = db.cursor()
        cursor.execute("INSERT INTO disponibilite (id_utilisateur, jour_semaine, heure_debut, heure_fin) VALUES (%s, %s, %s, %s)", (user_id, data.get('jour'), data.get('heure_debut'), data.get('heure_fin')))
        db.commit()
        cursor.close()
        return jsonify({'success': True})
    
    @app.route('/api/user/disponibilites/clear', methods=['DELETE'])
    def clear_disponibilites():
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from backend.models.user import User
        user = User(app.config['get_db']())
        user_id = user.verify_token(token)
        if not user_id:
            return jsonify({'error': 'Non autorise'}), 401
        db = app.config['get_db']()
        cursor = db.cursor()
        cursor.execute("DELETE FROM disponibilite WHERE id_utilisateur = %s", (user_id,))
        db.commit()
        cursor.close()
        return jsonify({'success': True})
    
    # ==================== WEBSOCKET ====================
    @socketio.on('join')
    def handle_join(data):
        conversation_id = data.get('conversation_id')
        if conversation_id:
            from flask_socketio import join_room
            join_room(f'conv_{conversation_id}')
    
    @socketio.on('leave')
    def handle_leave(data):
        conversation_id = data.get('conversation_id')
        if conversation_id:
            from flask_socketio import leave_room
            leave_room(f'conv_{conversation_id}')
    
    # ==================== PAGE D'ACCUEIL ====================
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Route non trouvee'}), 404
    
    socketio.init_app(app)
    return app, socketio
