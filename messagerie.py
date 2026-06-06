# messagerie.py — Back-end Messagerie
# Responsable : Chimed
# Projet : MentorLink — IFRI

from flask import Blueprint, request, jsonify, session
from flask_socketio import emit, join_room, leave_room
from datetime import datetime
import sqlite3

messagerie_bp = Blueprint('messagerie', __name__)

def get_db():
    conn = sqlite3.connect('mentorlink.db')
    conn.row_factory = sqlite3.Row
    return conn, conn.cursor()

@messagerie_bp.route('/api/conversations', methods=['GET'])
def get_conversations():
    if 'id_utilisateur' not in session:
        return jsonify({'succes': False, 'message': 'Non connecté'}), 401
    conn, cur = get_db()
    cur.execute('''
        SELECT
            c.id_conversation,
            CASE WHEN c.id_utilisateur_1 = ? THEN u2.id_utilisateur ELSE u1.id_utilisateur END AS id_interlocuteur,
            CASE WHEN c.id_utilisateur_1 = ? THEN u2.nom ELSE u1.nom END AS nom_interlocuteur,
            CASE WHEN c.id_utilisateur_1 = ? THEN u2.prenom ELSE u1.prenom END AS prenom_interlocuteur,
            CASE WHEN c.id_utilisateur_1 = ? THEN u2.photo_profil ELSE u1.photo_profil END AS photo_interlocuteur,
            c.date_dernier_msg,
            (SELECT m.contenu FROM message m WHERE m.id_conversation = c.id_conversation ORDER BY m.date_envoi DESC LIMIT 1) AS dernier_message,
            (SELECT COUNT(*) FROM message m WHERE m.id_conversation = c.id_conversation AND m.est_lu = FALSE AND m.id_expediteur != ?) AS messages_non_lus
        FROM conversation c
        JOIN utilisateur u1 ON c.id_utilisateur_1 = u1.id_utilisateur
        JOIN utilisateur u2 ON c.id_utilisateur_2 = u2.id_utilisateur
        WHERE c.id_utilisateur_1 = ? OR c.id_utilisateur_2 = ?
        ORDER BY c.date_dernier_msg DESC
    ''', (
        session['id_utilisateur'],
        session['id_utilisateur'],
        session['id_utilisateur'],
        session['id_utilisateur'],
        session['id_utilisateur'],
        session['id_utilisateur'],
        session['id_utilisateur'],
    ))
    conversations = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({'succes': True, 'conversations': conversations})

@messagerie_bp.route('/api/conversations', methods=['POST'])
def creer_conversation():
    if 'id_utilisateur' not in session:
        return jsonify({'succes': False}), 401
    data = request.get_json()
    id_destinataire = data.get('id_destinataire')
    if not id_destinataire:
        return jsonify({'succes': False, 'message': 'Destinataire manquant'}), 400
    conn, cur = get_db()
    cur.execute('''
        SELECT id_conversation FROM conversation
        WHERE (id_utilisateur_1 = ? AND id_utilisateur_2 = ?)
           OR (id_utilisateur_1 = ? AND id_utilisateur_2 = ?)
    ''', (session['id_utilisateur'], id_destinataire, id_destinataire, session['id_utilisateur']))
    conv = cur.fetchone()
    if conv:
        conn.close()
        return jsonify({'succes': True, 'id_conversation': conv['id_conversation']})
    cur.execute('''
        INSERT INTO conversation (id_utilisateur_1, id_utilisateur_2)
        VALUES (?, ?)
    ''', (session['id_utilisateur'], id_destinataire))
    id_conversation = cur.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'succes': True, 'id_conversation': id_conversation}), 201

@messagerie_bp.route('/api/messages/<int:id_conversation>', methods=['GET'])
def get_messages(id_conversation):
    if 'id_utilisateur' not in session:
        return jsonify({'succes': False}), 401
    conn, cur = get_db()
    cur.execute('''
        SELECT
            m.id_message,
            m.contenu,
            m.est_lu,
            m.date_envoi,
            m.id_expediteur,
            u.nom AS nom_expediteur,
            u.prenom AS prenom_expediteur,
            u.photo_profil AS photo_expediteur
        FROM message m
        JOIN utilisateur u ON m.id_expediteur = u.id_utilisateur
        WHERE m.id_conversation = ?
        ORDER BY m.date_envoi ASC
    ''', (id_conversation,))
    messages = [dict(row) for row in cur.fetchall()]
    cur.execute('''
        UPDATE message SET est_lu = TRUE
        WHERE id_conversation = ? AND id_expediteur != ? AND est_lu = FALSE
    ''', (id_conversation, session['id_utilisateur']))
    conn.commit()
    conn.close()
    return jsonify({'succes': True, 'messages': messages})

@messagerie_bp.route('/api/messages/<int:id_conversation>', methods=['POST'])
def envoyer_message(id_conversation):
    if 'id_utilisateur' not in session:
        return jsonify({'succes': False}), 401
    data = request.get_json()
    contenu = data.get('contenu')
    if not contenu or contenu.strip() == '':
        return jsonify({'succes': False, 'message': 'Message vide'}), 400
    conn, cur = get_db()
    cur.execute('''
        INSERT INTO message (id_conversation, id_expediteur, contenu)
        VALUES (?, ?, ?)
    ''', (id_conversation, session['id_utilisateur'], contenu.strip()))
    id_message = cur.lastrowid
    cur.execute('''
        UPDATE conversation SET date_dernier_msg = CURRENT_TIMESTAMP
        WHERE id_conversation = ?
    ''', (id_conversation,))
    conn.commit()
    conn.close()
    return jsonify({'succes': True, 'id_message': id_message}), 201

@messagerie_bp.route('/api/messages/<int:id_message>', methods=['DELETE'])
def supprimer_message(id_message):
    if 'id_utilisateur' not in session:
        return jsonify({'succes': False}), 401
    conn, cur = get_db()
    cur.execute('''
        SELECT * FROM message WHERE id_message = ? AND id_expediteur = ?
    ''', (id_message, session['id_utilisateur']))
    if not cur.fetchone():
        conn.close()
        return jsonify({'succes': False, 'message': 'Non autorisé'}), 403
    cur.execute('DELETE FROM message WHERE id_message = ?', (id_message,))
    conn.commit()
    conn.close()
    return jsonify({'succes': True, 'message': 'Message supprimé'})

@messagerie_bp.route('/api/conversations/<int:id_conversation>/lire', methods=['PUT'])
def marquer_comme_lu(id_conversation):
    if 'id_utilisateur' not in session:
        return jsonify({'succes': False}), 401
    conn, cur = get_db()
    cur.execute('''
        UPDATE message SET est_lu = TRUE
        WHERE id_conversation = ? AND id_expediteur != ? AND est_lu = FALSE
    ''', (id_conversation, session['id_utilisateur']))
    conn.commit()
    conn.close()
    return jsonify({'succes': True, 'message': 'Messages marqués comme lus'})

def on_connect():
    if 'id_utilisateur' in session:
        print(f"Utilisateur {session['id_utilisateur']} connecté")

def on_disconnect():
    if 'id_utilisateur' in session:
        print(f"Utilisateur {session['id_utilisateur']} déconnecté")

def on_rejoindre(data):
    id_conv = str(data['id_conversation'])
    join_room(id_conv)
    emit('statut', {'message': f"Connecté à la conversation {id_conv}"})

def on_envoyer_message(data):
    id_conversation = data['id_conversation']
    contenu = data['contenu']
    id_expediteur = data['id_expediteur']
    conn, cur = get_db()
    cur.execute('''
        INSERT INTO message (id_conversation, id_expediteur, contenu)
        VALUES (?, ?, ?)
    ''', (id_conversation, id_expediteur, contenu))
    id_message = cur.lastrowid
    conn.commit()
    cur.execute('''
        UPDATE conversation SET date_dernier_msg = CURRENT_TIMESTAMP
        WHERE id_conversation = ?
    ''', (id_conversation,))
    conn.commit()
    cur.execute('''
        SELECT nom, prenom, photo_profil FROM utilisateur WHERE id_utilisateur = ?
    ''', (id_expediteur,))
    exp = cur.fetchone()
    conn.close()
    emit('nouveau_message', {
        'id_message': id_message,
        'contenu': contenu,
        'id_expediteur': id_expediteur,
        'nom_expediteur': exp['nom'],
        'prenom_expediteur': exp['prenom'],
        'photo_expediteur': exp['photo_profil'],
        'date_envoi': datetime.now().strftime('%H:%M'),
        'est_lu': False
    }, room=str(id_conversation))

def on_ecriture(data):
    emit('afficher_ecriture', {
        'id_expediteur': data['id_expediteur']
    }, room=str(data['id_conversation']), include_self=False)

def on_quitter(data):
    leave_room(str(data['id_conversation']))

def init_socketio(socketio):
    socketio.on_event('connect', on_connect)
    socketio.on_event('disconnect', on_disconnect)
    socketio.on_event('rejoindre', on_rejoindre)
    socketio.on_event('envoyer_message', on_envoyer_message)
    socketio.on_event('en_train_ecrire', on_ecriture)
    socketio.on_event('quitter', on_quitter)