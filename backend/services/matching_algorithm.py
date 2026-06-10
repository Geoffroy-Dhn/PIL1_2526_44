# -*- coding: utf-8 -*-
class MatchingAlgorithm:
    def __init__(self, db):
        self.db = db
    
    def generate_matches_for_user(self, user_id):
        cursor = self.db.cursor()
        all_matches = []
        
        # Recuperer tous les autres utilisateurs actifs
        cursor.execute("""
            SELECT id_utilisateur, nom, prenom FROM utilisateur 
            WHERE id_utilisateur != %s AND est_actif = TRUE
        """, (user_id,))
        
        autres = cursor.fetchall()
        
        for autre in autres:
            autre_id = autre['id_utilisateur']
            
            # Calculer le score pour chaque paire
            score = self.calculate_match_score(user_id, autre_id)
            
            # Determiner les rôles
            mentor, mentore = self.determine_roles(user_id, autre_id)
            
            # Stocker le match même si score faible (on filtrera après)
            all_matches.append({
                'mentor_id': mentor,
                'mentore_id': mentore,
                'score': score['global'],
                'score_details': score,
                'autre_id': autre_id,
                'autre_nom': autre['nom'],
                'autre_prenom': autre['prenom']
            })
        
        cursor.close()
        
        # Trier par score decroissant
        all_matches.sort(key=lambda x: x['score'], reverse=True)
        
        # Garder le top 5 maximum (ou tous ceux avec score > 0)
        top_matches = [m for m in all_matches if m['score'] >= 30][:5]
        
        # Sauvegarder les matches dans la base
        saved_matches = []
        for match in top_matches:
            self.save_matching(match['mentor_id'], match['mentore_id'], match['score_details'])
            saved_matches.append({
                'mentor_id': match['mentor_id'],
                'mentore_id': match['mentore_id'],
                'score': match['score']
            })
        
        return saved_matches
    
    def calculate_match_score(self, user1_id, user2_id):
        cursor = self.db.cursor()
        
        # 1. Score competences (60%)
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM profil_competence pc1
            JOIN profil_competence pc2 ON pc1.id_competence = pc2.id_competence
            WHERE pc1.id_utilisateur = %s AND pc1.type_maitrise = 'fort'
            AND pc2.id_utilisateur = %s AND pc2.type_maitrise = 'faible'
        """, (user1_id, user2_id))
        result1 = cursor.fetchone()
        score1 = result1['count'] if result1 else 0
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM profil_competence pc1
            JOIN profil_competence pc2 ON pc1.id_competence = pc2.id_competence
            WHERE pc1.id_utilisateur = %s AND pc1.type_maitrise = 'fort'
            AND pc2.id_utilisateur = %s AND pc2.type_maitrise = 'faible'
        """, (user2_id, user1_id))
        result2 = cursor.fetchone()
        score2 = result2['count'] if result2 else 0
        
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM profil_competence WHERE id_utilisateur = %s AND type_maitrise = 'faible') as lacunes1,
                (SELECT COUNT(*) FROM profil_competence WHERE id_utilisateur = %s AND type_maitrise = 'faible') as lacunes2
        """, (user1_id, user2_id))
        lacunes = cursor.fetchone()
        lacunes1 = lacunes['lacunes1'] if lacunes else 1
        lacunes2 = lacunes['lacunes2'] if lacunes else 1
        
        score_direction1 = (score1 / max(lacunes2, 1)) * 100
        score_direction2 = (score2 / max(lacunes1, 1)) * 100
        competence_score = max(score_direction1, score_direction2)
        
        # 2. Score filière (10%)
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN u1.id_filiere = u2.id_filiere THEN 100
                    ELSE 50
                END as filiere_score
            FROM utilisateur u1, utilisateur u2
            WHERE u1.id_utilisateur = %s AND u2.id_utilisateur = %s
        """, (user1_id, user2_id))
        filiere_score = cursor.fetchone()['filiere_score']
        
        # 3. Score niveau (10%)
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN u1.niveau_etudes = u2.niveau_etudes THEN 100
                    ELSE 50
                END as niveau_score
            FROM utilisateur u1, utilisateur u2
            WHERE u1.id_utilisateur = %s AND u2.id_utilisateur = %s
        """, (user1_id, user2_id))
        niveau_score = cursor.fetchone()['niveau_score']
        
        # 4. Score disponibilites (20%)
        cursor.execute("""
            SELECT COUNT(*) as matching_slots
            FROM disponibilite d1
            JOIN disponibilite d2 ON 
                d1.jour_semaine = d2.jour_semaine
                AND d1.heure_debut < d2.heure_fin
                AND d1.heure_fin > d2.heure_debut
            WHERE d1.id_utilisateur = %s AND d2.id_utilisateur = %s
        """, (user1_id, user2_id))
        matching_slots = cursor.fetchone()['matching_slots']
        
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM disponibilite WHERE id_utilisateur = %s) as total1,
                (SELECT COUNT(*) FROM disponibilite WHERE id_utilisateur = %s) as total2
        """, (user1_id, user2_id))
        totals = cursor.fetchone()
        total_slots = max(totals['total1'], totals['total2'], 1)
        disponibilite_score = (matching_slots / total_slots) * 100
        
        cursor.close()
        
        # Ponderations : 60% competences, 10% filière, 10% niveau, 20% disponibilites
        global_score = (
            competence_score * 0.60 +
            filiere_score * 0.10 +
            niveau_score * 0.10 +
            disponibilite_score * 0.20
        )
        
        return {
            'global': round(global_score, 2),
            'competences': round(competence_score, 2),
            'filiere': round(filiere_score, 2),
            'niveau': round(niveau_score, 2),
            'disponibilite': round(disponibilite_score, 2)
        }
    
    def determine_roles(self, user1_id, user2_id):
        cursor = self.db.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM profil_competence pc1
            JOIN profil_competence pc2 ON pc1.id_competence = pc2.id_competence
            WHERE pc1.id_utilisateur = %s AND pc1.type_maitrise = 'fort'
            AND pc2.id_utilisateur = %s AND pc2.type_maitrise = 'faible'
        """, (user1_id, user2_id))
        user1_mentor_score = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM profil_competence pc1
            JOIN profil_competence pc2 ON pc1.id_competence = pc2.id_competence
            WHERE pc1.id_utilisateur = %s AND pc1.type_maitrise = 'fort'
            AND pc2.id_utilisateur = %s AND pc2.type_maitrise = 'faible'
        """, (user2_id, user1_id))
        user2_mentor_score = cursor.fetchone()['count']
        
        cursor.close()
        
        if user1_mentor_score >= user2_mentor_score:
            return user1_id, user2_id
        else:
            return user2_id, user1_id
    
    def save_matching(self, mentor_id, mentore_id, score):
        cursor = self.db.cursor()
        # Verifier si un match existe dejà dans cette direction
        cursor.execute("""
            SELECT id_matching FROM matching 
            WHERE id_mentor = %s AND id_mentore = %s
        """, (mentor_id, mentore_id))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE matching 
                SET score_global = %s, score_competences = %s, 
                    score_filiere = %s, score_disponibilite = %s,
                    date_modification = CURRENT_TIMESTAMP
                WHERE id_matching = %s
            """, (score['global'], score['competences'], score['filiere'], 
                  score['disponibilite'], existing['id_matching']))
        else:
            cursor.execute("""
                INSERT INTO matching (id_mentor, id_mentore, score_global, score_competences, 
                                     score_filiere, score_disponibilite, statut)
                VALUES (%s, %s, %s, %s, %s, %s, 'suggere')
            """, (mentor_id, mentore_id, score['global'], score['competences'], 
                  score['filiere'], score['disponibilite']))
        
        self.db.commit()
        cursor.close()
