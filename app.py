from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="mentorlink",
        user="postgres",
        password="votre_mot_de_passe",
        cursor_factory=RealDictCursor
    )

# -----------------------------------------------------------------------------
# ALGORITHME DE MATCHING PAR OFFRES / DEMANDES
# -----------------------------------------------------------------------------

def executer_matching_offres_demandes():
    """
    Parcourt toutes les offres et toutes les demandes actives pour trouver les correspondances
    sur les matières généralistes, calcule le score et alimente la table 'matching'.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 1. Récupérer toutes les offres actives avec leurs compétences associées
        cur.execute("""
            SELECT o.id_offre, o.id_utilisateur AS id_mentor, oc.id_competence
            FROM offre_mentorat o
            JOIN offre_competence oc ON o.id_offre = oc.id_offre
            WHERE o.statut = 'actif';
        """)
        offres = cur.fetchall()

        # 2. Récupérer toutes les demandes actives avec leurs compétences associées
        cur.execute("""
            SELECT d.id_demande, d.id_utilisateur AS id_mentore, dc.id_competence
            FROM demande_mentorat d
            JOIN demande_competence dc ON d.id_demande = dc.id_demande
            WHERE d.statut = 'actif';
        """)
        demandes = cur.fetchall()

        # 3. Comparer chaque offre avec chaque demande (Croisement)
        for offre in offres:
            for demande in demandes:
                # Sécurité : Un étudiant ne peut pas matcher avec lui-même
                if offre['id_mentor'] == demande['id_mentore']:
                    continue
                
                # Vérification de la matière commune
                if offre['id_competence'] == demande['id_competence']:
                    # Étant donné qu'on match par annonce précise (1 matière par offre/demande en général),
                    # le score de compétence est maximal (100 points) dès qu'il y a correspondance.
                    score_global = 100.0
                    score_competences = 100.0

                    # Insertion ou mise à jour (Upsert) dans la table matching
                    # On lie explicitement id_offre et id_demande comme demandé par votre BDD
                    cur.execute("""
                        INSERT INTO matching (
                            id_mentor, id_mentore, id_offre, id_demande, 
                            score_global, score_competences, score_disponibilite, score_filiere, 
                            statut, date_calcul
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, 0.0, 0.0, 'suggere', CURRENT_TIMESTAMP)
                        ON CONFLICT (id_mentor, id_mentore, id_offre, id_demande) 
                        DO UPDATE SET 
                            score_global = EXCLUDED.score_global,
                            score_competences = EXCLUDED.score_competences,
                            date_modification = CURRENT_TIMESTAMP;
                    """, (
                        offre['id_mentor'], 
                        demande['id_mentore'], 
                        offre['id_offre'], 
                        demande['id_demande'], 
                        score_global, 
                        score_competences
                    ))
                    
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erreur lors de l'exécution du matching : {e}")
    finally:
        cur.close()
        conn.close()


# -----------------------------------------------------------------------------
# ENDPOINTS API (ROUTES)
# -----------------------------------------------------------------------------

@app.route('/api/offres', methods=['POST'])
def creer_offre():
    """
    Route pour publier une Offre de mentorat (Formulaire précis et explicite)
    """
    data = request.get_json()
    id_utilisateur = data.get('id_utilisateur')
    id_competence = data.get('id_competence') # Le domaine généraliste choisi
    
    if not id_utilisateur or not id_competence:
        return jsonify({"error": "Données incomplètes."}), 400
        
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 1. Insertion dans la table offre_mentorat
        cur.execute("""
            INSERT INTO offre_mentorat (id_utilisateur, statut, date_creation)
            VALUES (%s, 'actif', CURRENT_TIMESTAMP) RETURNING id_offre;
        """, (id_utilisateur,))
        id_offre = cur.fetchone()['id_offre']
        
        # 2. Liaison avec la compétence dans offre_competence
        cur.execute("""
            INSERT INTO offre_competence (id_offre, id_competence)
            VALUES (%s, %s);
        """, (id_offre, id_competence))
        
        conn.commit()
        
        # 3. On lance le matching automatiquement en tâche de fond
        executer_matching_offres_demandes()
        
        return jsonify({"message": "Offre publiée avec succès !", "id_offre": id_offre}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/api/demandes', methods=['POST'])
def creer_demande():
    """
    Route pour publier une Demande de mentorat (Formulaire précis et explicite)
    """
    data = request.get_json()
    id_utilisateur = data.get('id_utilisateur')
    id_competence = data.get('id_competence') # Le domaine généraliste choisi
    
    if not id_utilisateur or not id_competence:
        return jsonify({"error": "Données incomplètes."}), 400
        
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 1. Insertion dans la table demande_mentorat
        cur.execute("""
            INSERT INTO demande_mentorat (id_utilisateur, statut, date_creation)
            VALUES (%s, 'actif', CURRENT_TIMESTAMP) RETURNING id_demande;
        """, (id_utilisateur,))
        id_demande = cur.fetchone()['id_demande']
        
        # 2. Liaison avec la compétence dans demande_competence
        cur.execute("""
            INSERT INTO demande_competence (id_demande, id_competence)
            VALUES (%s, %s);
        """, (id_demande, id_competence))
        
        conn.commit()
        
        # 3. On lance le matching automatiquement en tâche de fond
        executer_matching_offres_demandes()
        
        return jsonify({"message": "Demande publiée avec succès !", "id_demande": id_demande}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/api/suggestions/<int:id_utilisateur>', methods=['GET'])
def obtenir_suggestions(id_utilisateur):
    """
    Récupère les offres ou demandes compatibles triées par score.
    """
    role = request.args.get('role') # 'mentor' (on cherche des mentors) ou 'mentore' (on cherche des mentorés)
    
    if not role:
        return jsonify({"error": "Le paramètre 'role' est requis."}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        if role == 'mentor':
            # L'utilisateur connecté cherche des Offres faites par des Mentors
            cur.execute("""
                SELECT * FROM vue_matching_complet 
                WHERE id_mentore = %s AND statut = 'suggere'
                ORDER BY score_global DESC
            """, (id_utilisateur,))
        else:
            # L'utilisateur connecté cherche des Demandes faites par des Mentorés
            cur.execute("""
                SELECT * FROM vue_matching_complet 
                WHERE id_mentor = %s AND statut = 'suggere'
                ORDER BY score_global DESC
            """, (id_utilisateur,))
            
        return jsonify(cur.fetchall()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)