-- =============================================================================
--  IFRI_MentorLink — Base de données principale (Version PostgreSQL)
--  Projet intégrateur PIL1 2025-2026 | IFRI / Université d'Abomey-Calavi
--  VERSION AMÉLIORÉE AVEC TRIGGERS ET SUGGESTIONS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 0. NETTOYAGE DES ANCIENNES TABLES ET TYPES
-- -----------------------------------------------------------------------------
DROP VIEW IF EXISTS vue_apercu_conversations CASCADE;
DROP VIEW IF EXISTS vue_matching_complet CASCADE;
DROP VIEW IF EXISTS vue_lacunes CASCADE;
DROP VIEW IF EXISTS vue_points_forts CASCADE;
DROP VIEW IF EXISTS vue_profil_utilisateur CASCADE;

DROP TABLE IF EXISTS message CASCADE;
DROP TABLE IF EXISTS conversation CASCADE;
DROP TABLE IF EXISTS matching CASCADE;
DROP TABLE IF EXISTS demande_disponibilite CASCADE;
DROP TABLE IF EXISTS demande_competence CASCADE;
DROP TABLE IF EXISTS demande_mentorat CASCADE;
DROP TABLE IF EXISTS offre_disponibilite CASCADE;
DROP TABLE IF EXISTS offre_competence CASCADE;
DROP TABLE IF EXISTS offre_mentorat CASCADE;
DROP TABLE IF EXISTS disponibilite CASCADE;
DROP TABLE IF EXISTS profil_competence CASCADE;
DROP TABLE IF EXISTS utilisateur CASCADE;
DROP TABLE IF EXISTS competence CASCADE;
DROP TABLE IF EXISTS filiere CASCADE;
DROP TABLE IF EXISTS notification CASCADE;  -- NOUVELLE TABLE

DROP TYPE IF EXISTS type_niveau_etudes CASCADE;
DROP TYPE IF EXISTS type_role_applicatif CASCADE;
DROP TYPE IF EXISTS type_maitrise_competence CASCADE;
DROP TYPE IF EXISTS type_jour_semaine CASCADE;
DROP TYPE IF EXISTS type_format_session CASCADE;
DROP TYPE IF EXISTS type_statut_publication CASCADE;
DROP TYPE IF EXISTS type_statut_matching CASCADE;
DROP TYPE IF EXISTS type_notification CASCADE;  -- NOUVEAU TYPE

-- -----------------------------------------------------------------------------
-- ENUMS SPECIFIQUES POSTGRESQL
-- -----------------------------------------------------------------------------
CREATE TYPE type_niveau_etudes AS ENUM ('L1', 'L2', 'L3', 'M1', 'M2');
CREATE TYPE type_role_applicatif AS ENUM ('mentor', 'mentore', 'les_deux');
CREATE TYPE type_maitrise_competence AS ENUM ('fort', 'faible');
CREATE TYPE type_jour_semaine AS ENUM ('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche');
CREATE TYPE type_format_session AS ENUM ('presentiel', 'en_ligne', 'les_deux');
CREATE TYPE type_statut_publication AS ENUM ('active', 'pourvue', 'annulee');
CREATE TYPE type_statut_matching AS ENUM ('suggere', 'accepte', 'refuse', 'en_cours', 'termine');
CREATE TYPE type_notification AS ENUM ('message', 'match_suggere', 'match_accepte', 'rappel');  -- NOUVEAU


-- =============================================================================
-- 1. TABLE : filiere
-- =============================================================================
CREATE TABLE filiere (
    id_filiere      SERIAL,
    code_filiere    VARCHAR(20)     NOT NULL,   -- ex: 'IA', 'GL', 'SI', 'SE_IOT', 'IM'
    libelle         VARCHAR(100)    NOT NULL,   -- ex: 'Intelligence Artificielle'
    description     TEXT,

    CONSTRAINT pk_filiere       PRIMARY KEY (id_filiere),
    CONSTRAINT uq_filiere_code  UNIQUE      (code_filiere)
);


-- =============================================================================
-- 2. TABLE : competence
-- =============================================================================
CREATE TABLE competence (
    id_competence   SERIAL,
    nom             VARCHAR(100)    NOT NULL,   -- ex: 'Algorithmique', 'Base de données'
    categorie       VARCHAR(80),                -- ex: 'Informatique', 'Mathématiques'
    description     TEXT,

    CONSTRAINT pk_competence        PRIMARY KEY (id_competence),
    CONSTRAINT uq_competence_nom    UNIQUE      (nom)
);


-- =============================================================================
-- 3. TABLE : utilisateur (AMÉLIORÉE)
-- =============================================================================
CREATE TABLE utilisateur (
    id_utilisateur      SERIAL,

    -- Informations d'identité
    nom                 VARCHAR(80)         NOT NULL,
    prenom              VARCHAR(80)         NOT NULL,
    email               VARCHAR(180)        NOT NULL,
    telephone           VARCHAR(25)         NOT NULL,
    mot_de_passe        VARCHAR(255)        NOT NULL,   -- hashé bcrypt côté Python

    -- Profil
    photo_profil        VARCHAR(500),                  -- chemin ou URL de l'image
    bio                 TEXT,                          -- bio courte / centres d'intérêt
    niveau_etudes       type_niveau_etudes  NOT NULL DEFAULT 'L1',
    id_filiere          INT                 NOT NULL,

    -- Rôle applicatif
    role                type_role_applicatif NOT NULL DEFAULT 'les_deux',

    -- Session & authentification
    ml_token            VARCHAR(512),                  -- JWT actif
    mentorlink_session  VARCHAR(255),                  -- cookie de session de secours
    token_expiration    TIMESTAMP,                     -- date d'expiration du JWT

    -- Réinitialisation du mot de passe
    reset_token            VARCHAR(255),
    reset_token_expiration TIMESTAMP,

    -- NOUVEAU : date de dernière connexion
    date_derniere_connexion TIMESTAMP,

    -- Métadonnées
    est_actif           BOOLEAN             NOT NULL DEFAULT TRUE,
    date_inscription    TIMESTAMP           NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_modification   TIMESTAMP           NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_utilisateur           PRIMARY KEY (id_utilisateur),
    CONSTRAINT uq_utilisateur_email     UNIQUE      (email),
    CONSTRAINT uq_utilisateur_tel       UNIQUE      (telephone),
    CONSTRAINT fk_utilisateur_filiere   FOREIGN KEY (id_filiere)
                                        REFERENCES  filiere(id_filiere)
                                        ON UPDATE CASCADE
                                        ON DELETE RESTRICT
);


-- =============================================================================
-- 4. TABLE : profil_competence
-- =============================================================================
CREATE TABLE profil_competence (
    id_profil_competence    SERIAL,
    id_utilisateur          INT     NOT NULL,
    id_competence           INT     NOT NULL,
    type_maitrise           type_maitrise_competence NOT NULL,

    CONSTRAINT pk_profil_competence         PRIMARY KEY (id_profil_competence),
    CONSTRAINT uq_profil_comp_unique        UNIQUE (id_utilisateur, id_competence),

    CONSTRAINT fk_profil_comp_utilisateur   FOREIGN KEY (id_utilisateur)
                                            REFERENCES  utilisateur(id_utilisateur)
                                            ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_profil_comp_competence    FOREIGN KEY (id_competence)
                                            REFERENCES  competence(id_competence)
                                            ON UPDATE CASCADE ON DELETE RESTRICT
);


-- =============================================================================
-- 5. TABLE : disponibilite
-- =============================================================================
CREATE TABLE disponibilite (
    id_disponibilite     SERIAL,
    id_utilisateur       INT               NOT NULL,
    jour_semaine         type_jour_semaine NOT NULL,
    heure_debut          TIME              NOT NULL,
    heure_fin            TIME              NOT NULL,

    CONSTRAINT pk_disponibilite             PRIMARY KEY (id_disponibilite),
    CONSTRAINT uq_dispo_user_jour_heure     UNIQUE (id_utilisateur, jour_semaine, heure_debut),
    CONSTRAINT fk_disponibilite_utilisateur FOREIGN KEY (id_utilisateur)
                                            REFERENCES  utilisateur(id_utilisateur)
                                            ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chk_dispo_heures             CHECK (heure_fin > heure_debut)
);


-- =============================================================================
-- 6. TABLE : offre_mentorat
-- =============================================================================
CREATE TABLE offre_mentorat (
    id_offre            SERIAL,
    id_utilisateur      INT         NOT NULL, -- le mentor

    titre               VARCHAR(200)    NOT NULL,
    description         TEXT,
    format_session      type_format_session NOT NULL DEFAULT 'les_deux',
    statut              type_statut_publication NOT NULL DEFAULT 'active',

    date_publication    TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_modification   TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_offre_mentorat            PRIMARY KEY (id_offre),
    CONSTRAINT fk_offre_utilisateur         FOREIGN KEY (id_utilisateur)
                                            REFERENCES  utilisateur(id_utilisateur)
                                            ON UPDATE CASCADE ON DELETE CASCADE
);


-- =============================================================================
-- 7. TABLE : offre_competence
-- =============================================================================
CREATE TABLE offre_competence (
    id_offre_competence SERIAL,
    id_offre            INT     NOT NULL,
    id_competence       INT     NOT NULL,

    CONSTRAINT pk_offre_competence          PRIMARY KEY (id_offre_competence),
    CONSTRAINT uq_offre_comp                UNIQUE (id_offre, id_competence),
    CONSTRAINT fk_offre_comp_offre          FOREIGN KEY (id_offre)
                                            REFERENCES  offre_mentorat(id_offre)
                                            ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_offre_comp_competence     FOREIGN KEY (id_competence)
                                            REFERENCES  competence(id_competence)
                                            ON UPDATE CASCADE ON DELETE RESTRICT
);


-- =============================================================================
-- 8. TABLE : offre_disponibilite
-- =============================================================================
CREATE TABLE offre_disponibilite (
    id_offre_dispo      SERIAL,
    id_offre            INT               NOT NULL,
    jour_semaine         type_jour_semaine NOT NULL,
    heure_debut          TIME              NOT NULL,
    heure_fin            TIME              NOT NULL,

    CONSTRAINT pk_offre_disponibilite       PRIMARY KEY (id_offre_dispo),
    CONSTRAINT uq_offre_dispo               UNIQUE (id_offre, jour_semaine, heure_debut),
    CONSTRAINT fk_offre_dispo_offre          FOREIGN KEY (id_offre)
                                            REFERENCES  offre_mentorat(id_offre)
                                            ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chk_offre_dispo_heures       CHECK (heure_fin > heure_debut)
);


-- =============================================================================
-- 9. TABLE : demande_mentorat
-- =============================================================================
CREATE TABLE demande_mentorat (
    id_demande          SERIAL,
    id_utilisateur      INT         NOT NULL, -- le mentoré

    titre               VARCHAR(200)    NOT NULL,
    description         TEXT,
    format_session      type_format_session NOT NULL DEFAULT 'les_deux',
    statut              type_statut_publication NOT NULL DEFAULT 'active',

    date_publication    TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_modification   TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_demande_mentorat          PRIMARY KEY (id_demande),
    CONSTRAINT fk_demande_utilisateur       FOREIGN KEY (id_utilisateur)
                                            REFERENCES  utilisateur(id_utilisateur)
                                            ON UPDATE CASCADE ON DELETE CASCADE
);


-- =============================================================================
-- 10. TABLE : demande_competence
-- =============================================================================
CREATE TABLE demande_competence (
    id_demande_competence   SERIAL,
    id_demande              INT     NOT NULL,
    id_competence           INT     NOT NULL,

    CONSTRAINT pk_demande_competence        PRIMARY KEY (id_demande_competence),
    CONSTRAINT uq_demande_comp              UNIQUE (id_demande, id_competence),
    CONSTRAINT fk_demande_comp_demande      FOREIGN KEY (id_demande)
                                            REFERENCES  demande_mentorat(id_demande)
                                            ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_demande_comp_competence   FOREIGN KEY (id_competence)
                                            REFERENCES  competence(id_competence)
                                            ON UPDATE CASCADE ON DELETE RESTRICT
);


-- =============================================================================
-- 11. TABLE : demande_disponibilite
-- =============================================================================
CREATE TABLE demande_disponibilite (
    id_demande_dispo    SERIAL,
    id_demande          INT               NOT NULL,
    jour_semaine         type_jour_semaine NOT NULL,
    heure_debut          TIME              NOT NULL,
    heure_fin            TIME              NOT NULL,

    CONSTRAINT pk_demande_disponibilite     PRIMARY KEY (id_demande_dispo),
    CONSTRAINT uq_demande_dispo             UNIQUE (id_demande, jour_semaine, heure_debut),
    CONSTRAINT fk_demande_dispo_demande     FOREIGN KEY (id_demande)
                                            REFERENCES  demande_mentorat(id_demande)
                                            ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chk_demande_dispo_heures     CHECK (heure_fin > heure_debut)
);


-- =============================================================================
-- 12. TABLE : matching
-- =============================================================================
CREATE TABLE matching (
    id_matching         SERIAL,
    id_mentor           INT           NOT NULL,
    id_mentore          INT           NOT NULL,
    id_offre            INT,
    id_demande          INT,

    score_global        DECIMAL(5,2)    NOT NULL DEFAULT 0.00,
    score_competences   DECIMAL(5,2)    NOT NULL DEFAULT 0.00,
    score_disponibilite DECIMAL(5,2)    NOT NULL DEFAULT 0.00,
    score_filiere       DECIMAL(5,2)    NOT NULL DEFAULT 0.00,

    statut              type_statut_matching NOT NULL DEFAULT 'suggere',
    date_calcul         TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_modification   TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_matching                  PRIMARY KEY (id_matching),
    CONSTRAINT uq_matching_pair             UNIQUE (id_mentor, id_mentore, id_offre, id_demande),
    CONSTRAINT fk_matching_mentor           FOREIGN KEY (id_mentor)
                                            REFERENCES  utilisateur(id_utilisateur)
                                            ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_matching_mentore          FOREIGN KEY (id_mentore)
                                            REFERENCES  utilisateur(id_utilisateur)
                                            ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_matching_offre            FOREIGN KEY (id_offre)
                                            REFERENCES  offre_mentorat(id_offre)
                                            ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_matching_demande          FOREIGN KEY (id_demande)
                                            REFERENCES  demande_mentorat(id_demande)
                                            ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT chk_matching_no_self         CHECK (id_mentor <> id_mentore),
    CONSTRAINT chk_score_global             CHECK (score_global BETWEEN 0 AND 100),
    CONSTRAINT chk_score_competences        CHECK (score_competences BETWEEN 0 AND 100),
    CONSTRAINT chk_score_disponibilite      CHECK (score_disponibilite BETWEEN 0 AND 100),
    CONSTRAINT chk_score_filiere            CHECK (score_filiere BETWEEN 0 AND 100)
);


-- =============================================================================
-- 13. TABLE : conversation
-- =============================================================================
CREATE TABLE conversation (
    id_conversation     SERIAL,
    id_utilisateur_1    INT    NOT NULL,
    id_utilisateur_2    INT    NOT NULL,
    id_matching         INT,

    date_creation       TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_dernier_msg    TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_conversation              PRIMARY KEY (id_conversation),
    CONSTRAINT fk_conversation_user1        FOREIGN KEY (id_utilisateur_1)
                                            REFERENCES  utilisateur(id_utilisateur)
                                            ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_conversation_user2        FOREIGN KEY (id_utilisateur_2)
                                            REFERENCES  utilisateur(id_utilisateur)
                                            ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_conversation_matching     FOREIGN KEY (id_matching)
                                            REFERENCES  matching(id_matching)
                                            ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT chk_conversation_no_self    CHECK (id_utilisateur_1 <> id_utilisateur_2)
);

-- Index unique Postgres pour éviter les doublons de paires
CREATE UNIQUE INDEX uq_conversation_pair_idx ON conversation (
    (LEAST(id_utilisateur_1, id_utilisateur_2)), 
    (GREATEST(id_utilisateur_1, id_utilisateur_2))
);


-- =============================================================================
-- 14. TABLE : message (AMÉLIORÉE)
-- =============================================================================
CREATE TABLE message (
    id_message          SERIAL,
    id_conversation     INT     NOT NULL,
    id_expediteur       INT     NOT NULL,

    contenu             TEXT            NOT NULL,
    piece_jointe        VARCHAR(500),              -- NOUVEAU : pour les fichiers joints
    est_lu              BOOLEAN         NOT NULL DEFAULT FALSE,
    date_envoi          TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_message                   PRIMARY KEY (id_message),
    CONSTRAINT fk_message_conversation      FOREIGN KEY (id_conversation)
                                            REFERENCES  conversation(id_conversation)
                                            ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_message_expediteur        FOREIGN KEY (id_expediteur)
                                            REFERENCES  utilisateur(id_utilisateur)
                                            ON UPDATE CASCADE ON DELETE CASCADE
);


-- =============================================================================
-- 15. NOUVELLE TABLE : notification
-- =============================================================================
CREATE TABLE notification (
    id_notification     SERIAL,
    id_utilisateur      INT         NOT NULL,
    type_notification   type_notification NOT NULL,
    titre               VARCHAR(200)    NOT NULL,
    contenu             TEXT            NOT NULL,
    est_lue             BOOLEAN         NOT NULL DEFAULT FALSE,
    data_json           JSONB,                       -- Données supplémentaires en JSON
    date_creation       TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_notification            PRIMARY KEY (id_notification),
    CONSTRAINT fk_notification_utilisateur FOREIGN KEY (id_utilisateur)
                                           REFERENCES utilisateur(id_utilisateur)
                                           ON UPDATE CASCADE ON DELETE CASCADE
);

-- Index pour les notifications non lues
CREATE INDEX idx_notifications_non_lues ON notification(id_utilisateur, est_lue, date_creation);


-- =============================================================================
-- TRIGGER : Mise à jour automatique de date_modification sur utilisateur
-- =============================================================================
CREATE OR REPLACE FUNCTION update_utilisateur_modification()
RETURNS TRIGGER AS $$
BEGIN
    NEW.date_modification = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_utilisateur_modification
BEFORE UPDATE ON utilisateur
FOR EACH ROW
EXECUTE FUNCTION update_utilisateur_modification();


-- =============================================================================
-- TRIGGER : Mise à jour automatique de date_dernier_msg sur conversation
-- =============================================================================
CREATE OR REPLACE FUNCTION update_conversation_last_msg()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversation 
    SET date_dernier_msg = NEW.date_envoi
    WHERE id_conversation = NEW.id_conversation;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_conversation_last_msg
AFTER INSERT ON message
FOR EACH ROW
EXECUTE FUNCTION update_conversation_last_msg();


-- =============================================================================
-- TRIGGER : Mise à jour automatique de date_modification sur matching
-- =============================================================================
CREATE OR REPLACE FUNCTION update_matching_modification()
RETURNS TRIGGER AS $$
BEGIN
    NEW.date_modification = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_matching_modification
BEFORE UPDATE ON matching
FOR EACH ROW
EXECUTE FUNCTION update_matching_modification();


-- =============================================================================
-- TRIGGER : Création automatique de notification lors d'un nouveau match
-- =============================================================================
CREATE OR REPLACE FUNCTION notify_new_match()
RETURNS TRIGGER AS $$
BEGIN
    -- Notification pour le mentor
    INSERT INTO notification (id_utilisateur, type_notification, titre, contenu, data_json)
    VALUES (
        NEW.id_mentor,
        'match_suggere',
        'Nouveau match suggéré !',
        'Un mentoré a été matché avec vous. Consultez les détails.',
        jsonb_build_object('matching_id', NEW.id_matching, 'role', 'mentor')
    );
    
    -- Notification pour le mentoré
    INSERT INTO notification (id_utilisateur, type_notification, titre, contenu, data_json)
    VALUES (
        NEW.id_mentore,
        'match_suggere',
        'Nouveau match suggéré !',
        'Un mentor a été matché avec vous. Consultez les détails.',
        jsonb_build_object('matching_id', NEW.id_matching, 'role', 'mentore')
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_notify_new_match
AFTER INSERT ON matching
FOR EACH ROW
WHEN (NEW.statut = 'suggere')
EXECUTE FUNCTION notify_new_match();


-- =============================================================================
-- DONNÉES DE RÉFÉRENCE — Jeu de données initial
-- =============================================================================

-- Filières IFRI
INSERT INTO filiere (code_filiere, libelle, description) VALUES
('IA',     'Intelligence Artificielle',             'Machine Learning, Deep Learning, IA appliquée'),
('GL',     'Génie Logiciel',                        'Conception, architecture et qualité logicielle'),
('SI',     'Systèmes d''Information',               'Gestion et analyse des systèmes d''information'),
('SE_IOT', 'Systèmes Embarqués & IoT',              'Microcontrôleurs, capteurs, objets connectés'),
('IM',     'Ingénierie Mathématiques',              'Mathématiques appliquées à l''informatique');

-- Compétences / Matières
INSERT INTO competence (nom, categorie) VALUES
('Algorithmique et structures de données',  'Informatique'),
('Programmation Python',                    'Informatique'),
('Programmation C / C++',                   'Informatique'),
('Développement web (HTML/CSS/JS)',          'Informatique'),
('Bases de données et SQL',                 'Informatique'),
('Systèmes d''exploitation Linux',          'Informatique'),
('Réseaux informatiques',                   'Informatique'),
('Génie logiciel et UML',                   'Informatique'),
('Sécurité informatique',                   'Informatique'),
('Intelligence artificielle',               'Informatique'),
('Machine Learning',                        'Informatique'),
('Développement mobile',                    'Informatique'),
('Analyse mathématique',                    'Mathématiques'),
('Algèbre linéaire',                        'Mathématiques'),
('Probabilités et statistiques',            'Mathématiques'),
('Mathématiques discrètes',                 'Mathématiques'),
('Recherche opérationnelle',                'Mathématiques'),
('Communication et expression écrite',      'Transversal'),
('Anglais technique',                       'Transversal'),
('Gestion de projet (Trello / Git)',         'Transversal');


-- =============================================================================
-- VUES UTILES
-- =============================================================================

-- Vue : profil complet
CREATE VIEW vue_profil_utilisateur AS
SELECT
    u.id_utilisateur,
    u.nom,
    u.prenom,
    u.email,
    u.telephone,
    u.photo_profil,
    u.bio,
    u.niveau_etudes,
    u.role,
    u.est_actif,
    u.date_inscription,
    u.date_derniere_connexion,
    f.code_filiere,
    f.libelle AS libelle_filiere
FROM utilisateur u
JOIN filiere f ON u.id_filiere = f.id_filiere;

-- Vue : points forts
CREATE VIEW vue_points_forts AS
SELECT
    pc.id_utilisateur,
    u.nom,
    u.prenom,
    c.id_competence,
    c.nom          AS nom_competence,
    c.categorie
FROM profil_competence pc
JOIN utilisateur  u ON pc.id_utilisateur  = u.id_utilisateur
JOIN competence   c ON pc.id_competence   = c.id_competence
WHERE pc.type_maitrise = 'fort';

-- Vue : lacunes
CREATE VIEW vue_lacunes AS
SELECT
    pc.id_utilisateur,
    u.nom,
    u.prenom,
    c.id_competence,
    c.nom          AS nom_competence,
    c.categorie
FROM profil_competence pc
JOIN utilisateur  u ON pc.id_utilisateur  = u.id_utilisateur
JOIN competence   c ON pc.id_competence   = c.id_competence
WHERE pc.type_maitrise = 'faible';

-- Vue : résultats de matching complets
CREATE VIEW vue_matching_complet AS
SELECT
    m.id_matching,
    m.score_global,
    m.score_competences,
    m.score_disponibilite,
    m.score_filiere,
    m.statut,
    m.date_calcul,
    -- Mentor
    mentor.id_utilisateur   AS id_mentor,
    mentor.nom               AS nom_mentor,
    mentor.prenom           AS prenom_mentor,
    mentor.photo_profil     AS photo_mentor,
    f_mentor.libelle        AS filiere_mentor,
    mentor.niveau_etudes    AS niveau_mentor,
    -- Mentoré
    mentore.id_utilisateur  AS id_mentore,
    mentore.nom             AS nom_mentore,
    mentore.prenom          AS prenom_mentore,
    mentore.photo_profil    AS photo_mentore,
    f_mentore.libelle       AS filiere_mentore,
    mentore.niveau_etudes   AS niveau_mentore
FROM matching m
JOIN utilisateur mentor  ON m.id_mentor  = mentor.id_utilisateur
JOIN utilisateur mentore ON m.id_mentore = mentore.id_utilisateur
JOIN filiere f_mentor    ON mentor.id_filiere  = f_mentor.id_filiere
JOIN filiere f_mentore   ON mentore.id_filiere = f_mentore.id_filiere;

-- Vue : aperçu conversations (AMÉLIORÉE)
CREATE VIEW vue_apercu_conversations AS
SELECT
    c.id_conversation,
    c.id_utilisateur_1,
    c.id_utilisateur_2,
    c.date_dernier_msg,
    last_msg.contenu        AS dernier_message,
    last_msg.id_expediteur  AS expediteur_dernier_msg,
    last_msg.date_envoi     AS date_dernier_message,
    (
        SELECT COUNT(*)
        FROM message msg2
        WHERE msg2.id_conversation = c.id_conversation
          AND msg2.est_lu = FALSE
          AND msg2.id_expediteur != 
              (CASE WHEN c.id_utilisateur_1 = current_setting('app.current_user_id', TRUE)::int 
               THEN c.id_utilisateur_2 ELSE c.id_utilisateur_1 END)
    )                       AS messages_non_lus
FROM conversation c
LEFT JOIN message last_msg ON last_msg.id_message = (
    SELECT MAX(id_message)
    FROM message
    WHERE id_conversation = c.id_conversation
);

-- Vue : notifications non lues
CREATE VIEW vue_notifications_non_lues AS
SELECT
    n.id_notification,
    n.id_utilisateur,
    n.type_notification,
    n.titre,
    n.contenu,
    n.data_json,
    n.date_creation
FROM notification n
WHERE n.est_lue = FALSE
ORDER BY n.date_creation DESC;
