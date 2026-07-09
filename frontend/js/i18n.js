// Internationalization (i18n) for IFRI_MentorLink
// Supports French (fr) and English (en)

const i18nDictionary = {
    fr: {
        // Common & Navbar
        "nav_dashboard": "Tableau de bord",
        "nav_offres": "Offres/Demandes",
        "nav_matching": "Matching",
        "nav_profil": "Mon profil",
        "nav_messages": "Messages",
        "nav_logout": "Déconnexion",
        "nav_login": "Connexion",

        // index.html
        "hero_title": "🏫 IFRI_MentorLink",
        "hero_subtitle": "La plateforme de mentorat d'excellence pour tous les étudiants et mentors du monde entier.",
        "hero_desc": "Mettez en relation vos compétences et vos besoins académiques, dépassez les frontières et réussissez ensemble.",
        "btn_start": "🔐 Commencer l'aventure",
        "features_title": "Pourquoi choisir IFRI_MentorLink ?",
        "feature_1": "Créez votre profil étudiant personnalisé en quelques clics",
        "feature_2": "Définissez précisément vos compétences (points forts) et lacunes",
        "feature_3": "Publiez et consultez des offres ou demandes de mentorat",
        "feature_4": "Algorithme de matching intelligent et ultra-précis",
        "feature_5": "Messagerie instantanée sécurisée intégrée",

        // login.html
        "login_title": "🏫 IFRI_MentorLink",
        "login_subtitle": "Mettez en relation mentors et mentorés du monde entier",
        "label_email": "📧 Email",
        "label_password": "🔒 Mot de passe",
        "btn_login": "Se connecter",
        "forgot_password": "Mot de passe oublié ?",
        "no_account": "Pas encore de compte ?",
        "register_now": "S'inscrire",
        "register_title": "Créer un compte",
        "label_nom": "👤 Nom",
        "label_prenom": "👤 Prénom",
        "label_phone": "📱 Téléphone",
        "label_filiere": "🏫 Filière",
        "label_niveau": "📚 Niveau",
        "choose_filiere": "Choisir une filière...",
        "btn_register": "S'inscrire",
        "already_account": "Déjà un compte ?",
        "info_note": "💡 Après inscription, vous pourrez :<br>• Définir vos compétences pour être mentor<br>• Définir vos lacunes pour trouver un mentor<br>• Publier des offres et demandes de mentorat",
        "modal_forgot_title": "🔐 Mot de passe oublié",
        "modal_forgot_desc": "Saisissez votre adresse email pour recevoir un lien de réinitialisation.",
        "btn_send_reset": "Envoyer le lien de réinitialisation",

        // dashboard.html
        "dashboard_welcome": "Bienvenue !",
        "dashboard_subtitle": "Retrouvez ici un résumé de votre activité sur IFRI_MentorLink",
        "stat_offres": "Offres publiées",
        "stat_demandes": "Demandes publiées",
        "stat_matches": "Matches suggérés",
        "stat_messages": "Messages non lus",
        "action_publish": "📢 Publier une offre/demande",
        "action_matches": "🔍 Voir mes matches",
        "action_profile": "✏️ Compléter mon profil",
        "action_messages": "💬 Voir mes messages",
        "confirm_logout": "Êtes-vous sûr(e) de vouloir vous déconnecter ?",

        // offres_demandes.html
        "publish_offre_title": "📢 Publier une offre",
        "publish_demande_title": "🙏 Publier une demande",
        "role_mentor": "Mentor",
        "role_mentore": "Mentoré",
        "label_title_field": "Titre",
        "label_competence_field": "Compétence",
        "label_description_field": "Description",
        "label_format_field": "Format",
        "choose_option": "Choisir...",
        "format_presentiel": "Présentiel",
        "format_online": "En ligne",
        "format_both": "Les deux",
        "btn_publish_offre": "Publier l'offre",
        "btn_publish_demande": "Publier la demande",
        "my_offres_title": "📋 Mes offres",
        "my_demandes_title": "📋 Mes demandes",
        "no_offres": "Aucune offre publiée pour le moment.",
        "no_demandes": "Aucune demande publiée pour le moment.",
        "alert_published": "Publié avec succès !",

        // matching.html
        "matching_title": "🔍 Suggestions de mentorat",
        "loading_matches": "Chargement des matches...",
        "generate_matches_btn": "🔄 Générer de nouveaux matches",
        "no_matches_found": "🤝 Aucun match pour le moment",
        "no_matches_sub": "Complétez votre profil et générez des matches pour voir les suggestions.",
        "score_compatibility": "Score de compatibilité",
        "common_subjects": "📚 Matières en commun :",
        "common_dispos": "⏰ Disponibilités communes :",
        "score_details": "🎯 Détails du score :",
        "score_detail_comp": "Compétences",
        "score_detail_filiere": "Filière",
        "score_detail_dispo": "Disponibilités",
        "btn_contact_user": "Contacter",
        "no_common_comp": "Aucune compétence en commun",
        "no_common_dispos": "Aucune disponibilité commune",
        "generating": "🔄 Génération...",

        // messages.html
        "conversations_title": "💬 Conversations",
        "btn_refresh": "🔄 Actualiser",
        "no_conversations": "💬 Aucune conversation",
        "select_conv_placeholder": "🤝 Sélectionnez une conversation",
        "msg_input_placeholder": "Écrivez votre message...",
        "error_sending": "Erreur lors de l'envoi du message",

        // profil.html
        "profil_title": "Mon Profil - IFRI_MentorLink",
        "loading_profile": "⏳ Chargement du profil...",
        "personal_info": "📋 Informations personnelles",
        "label_phone_profil": "Téléphone",
        "label_niveau_profil": "Niveau",
        "label_filiere_profil": "Filière",
        "label_member_since": "Membre depuis",
        "not_provided": "Non renseigné",
        "points_forts": "⭐ Points forts (Compétences à enseigner)",
        "lacunes": "📚 Lacunes (Matières à apprendre)",
        "no_points_forts": "Aucun point fort défini pour le moment.",
        "no_lacunes": "Aucune lacune définie pour le moment.",
        "disponibilites_title": "⏰ Disponibilités",
        "no_dispos": "Aucune disponibilité renseignée.",
        "bio_title": "📝 Biographie",
        "no_bio": "Aucune biographie rédigée.",
        "btn_edit_profile": "✏️ Modifier mon profil",
        "edit_profile_title": "Modifier mon profil",
        "label_photo_url": "📸 Photo de profil (URL)",
        "add_competence_btn": "+ Ajouter",
        "add_dispo_btn": "+ Ajouter une disponibilité",
        "btn_save_profile": "💾 Enregistrer",
        "btn_cancel": "❌ Annuler",
        "confirm_delete_comp": "Voulez-vous vraiment supprimer cette compétence ?",
        "profile_updated": "✅ Profil mis à jour avec succès !",

        // reset-password.html
        "reset_pwd_title": "🔒 Réinitialisation du mot de passe",
        "label_new_pwd": "🔑 Nouveau mot de passe",
        "btn_reset_pwd": "Changer le mot de passe",
        "back_to_login": "Retour à la connexion",
        "pwd_too_short": "Le mot de passe doit contenir au moins 6 caractères",
        "pwd_reset_success": "Mot de passe modifié avec succès ! Redirection..."
    },
    en: {
        // Common & Navbar
        "nav_dashboard": "Dashboard",
        "nav_offres": "Offers/Requests",
        "nav_matching": "Matching",
        "nav_profil": "My Profile",
        "nav_messages": "Messages",
        "nav_logout": "Log Out",
        "nav_login": "Login",

        // index.html
        "hero_title": "🏫 IFRI_MentorLink",
        "hero_subtitle": "The premiere mentoring platform for students and mentors worldwide.",
        "hero_desc": "Match your skills and academic needs, bridge borders, and succeed together.",
        "btn_start": "🔐 Start the Journey",
        "features_title": "Why choose IFRI_MentorLink?",
        "feature_1": "Create your customized student profile in seconds",
        "feature_2": "Define precisely your strengths (skills) and areas of improvement",
        "feature_3": "Publish and search mentoring offers and requests",
        "feature_4": "Intelligent and highly accurate matching algorithm",
        "feature_5": "Built-in secure instant messaging",

        // login.html
        "login_title": "🏫 IFRI_MentorLink",
        "login_subtitle": "Connect mentors and mentees from all around the world",
        "label_email": "📧 Email",
        "label_password": "🔒 Password",
        "btn_login": "Log In",
        "forgot_password": "Forgot Password?",
        "no_account": "Don't have an account?",
        "register_now": "Sign Up",
        "register_title": "Create an Account",
        "label_nom": "👤 Last Name",
        "label_prenom": "👤 First Name",
        "label_phone": "📱 Phone Number",
        "label_filiere": "🏫 Major / Program",
        "label_niveau": "📚 Academic Level",
        "choose_filiere": "Choose a program...",
        "btn_register": "Register",
        "already_account": "Already have an account?",
        "info_note": "💡 After registration, you will be able to:<br>• Set your strengths to become a mentor<br>• Set your weaknesses to find a mentor<br>• Publish mentoring offers and requests",
        "modal_forgot_title": "🔐 Forgot Password",
        "modal_forgot_desc": "Enter your email address to receive a password reset link.",
        "btn_send_reset": "Send Reset Link",

        // dashboard.html
        "dashboard_welcome": "Welcome!",
        "dashboard_subtitle": "Find a summary of your activity on IFRI_MentorLink here",
        "stat_offres": "Offers published",
        "stat_demandes": "Requests published",
        "stat_matches": "Suggested matches",
        "stat_messages": "Unread messages",
        "action_publish": "📢 Publish an offer/request",
        "action_matches": "🔍 See my matches",
        "action_profile": "✏️ Complete my profile",
        "action_messages": "💬 See my messages",
        "confirm_logout": "Are you sure you want to log out?",

        // offres_demandes.html
        "publish_offre_title": "📢 Publish an Offer",
        "publish_demande_title": "🙏 Publish a Request",
        "role_mentor": "Mentor",
        "role_mentore": "Mentee",
        "label_title_field": "Title",
        "label_competence_field": "Skill / Subject",
        "label_description_field": "Description",
        "label_format_field": "Format",
        "choose_option": "Choose...",
        "format_presentiel": "In person",
        "format_online": "Online",
        "format_both": "Both",
        "btn_publish_offre": "Publish Offer",
        "btn_publish_demande": "Publish Request",
        "my_offres_title": "📋 My Offers",
        "my_demandes_title": "📋 My Requests",
        "no_offres": "No offers published yet.",
        "no_demandes": "No requests published yet.",
        "alert_published": "Published successfully!",

        // matching.html
        "matching_title": "🔍 Mentoring Suggestions",
        "loading_matches": "Loading matches...",
        "generate_matches_btn": "🔄 Generate New Matches",
        "no_matches_found": "🤝 No matches at the moment",
        "no_matches_sub": "Complete your profile and generate matches to see suggestions.",
        "score_compatibility": "Compatibility Score",
        "common_subjects": "📚 Shared subjects:",
        "common_dispos": "⏰ Shared availabilities:",
        "score_details": "🎯 Score details:",
        "score_detail_comp": "Skills",
        "score_detail_filiere": "Major",
        "score_detail_dispo": "Availabilities",
        "btn_contact_user": "Contact",
        "no_common_comp": "No shared skills",
        "no_common_dispos": "No shared availabilities",
        "generating": "🔄 Generating...",

        // messages.html
        "conversations_title": "💬 Conversations",
        "btn_refresh": "🔄 Refresh",
        "no_conversations": "💬 No conversations yet",
        "select_conv_placeholder": "🤝 Select a conversation",
        "msg_input_placeholder": "Type your message...",
        "error_sending": "Error sending message",

        // profil.html
        "profil_title": "My Profile - IFRI_MentorLink",
        "loading_profile": "⏳ Loading profile...",
        "personal_info": "📋 Personal Information",
        "label_phone_profil": "Phone",
        "label_niveau_profil": "Academic Level",
        "label_filiere_profil": "Major",
        "label_member_since": "Member since",
        "not_provided": "Not provided",
        "points_forts": "⭐ Strengths (Skills you can teach)",
        "lacunes": "📚 Weaknesses (Subjects you want to learn)",
        "no_points_forts": "No strengths defined yet.",
        "no_lacunes": "No weaknesses defined yet.",
        "disponibilites_title": "⏰ Availabilities",
        "no_dispos": "No availabilities defined.",
        "bio_title": "📝 Biography",
        "no_bio": "No biography written yet.",
        "btn_edit_profile": "✏️ Edit My Profile",
        "edit_profile_title": "Edit My Profile",
        "label_photo_url": "📸 Profile Photo (URL)",
        "add_competence_btn": "+ Add",
        "add_dispo_btn": "+ Add Availability",
        "btn_save_profile": "💾 Save Profile",
        "btn_cancel": "❌ Cancel",
        "confirm_delete_comp": "Do you really want to remove this skill?",
        "profile_updated": "✅ Profile updated successfully!",

        // reset-password.html
        "reset_pwd_title": "🔒 Password Reset",
        "label_new_pwd": "🔑 New Password",
        "btn_reset_pwd": "Change Password",
        "back_to_login": "Back to Login",
        "pwd_too_short": "Password must be at least 6 characters long",
        "pwd_reset_success": "Password successfully updated! Redirecting..."
    }
};

// Get current selected language
function getCurrentLanguage() {
    let lang = localStorage.getItem('lang');
    if (!lang) {
        lang = navigator.language || navigator.userLanguage;
        lang = lang.startsWith('en') ? 'en' : 'fr'; // default to French
    }
    return lang;
}

// Set application language and translate
function setLanguage(lang) {
    localStorage.setItem('lang', lang);
    translatePage();
    // Update language selectors
    const selector = document.getElementById('langSelect');
    if (selector) selector.value = lang;
}

// Function to translate the page based on data-i18n attributes
function translatePage() {
    const lang = getCurrentLanguage();
    const translations = i18nDictionary[lang];

    if (!translations) return;

    // Find all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[key]) {
            // Check if element has inputs/children we shouldn't overwrite completely
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.value = translations[key];
            } else {
                element.innerHTML = translations[key];
            }
        }
    });

    // Translate placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        if (translations[key]) {
            element.setAttribute('placeholder', translations[key]);
        }
    });

    // Translate titles
    document.querySelectorAll('[data-i18n-title]').forEach(element => {
        const key = element.getAttribute('data-i18n-title');
        if (translations[key]) {
            element.setAttribute('title', translations[key]);
        }
    });
}

// Auto inject language selector in navigation bar
function injectLanguageSelector() {
    const navLinks = document.querySelector('.nav-links');
    if (navLinks && !document.getElementById('langSelectContainer')) {
        const container = document.createElement('div');
        container.id = 'langSelectContainer';
        container.style.display = 'inline-flex';
        container.style.alignItems = 'center';
        container.style.marginLeft = '20px';
        container.style.background = '#f1f3f5';
        container.style.borderRadius = '8px';
        container.style.padding = '4px 8px';

        const select = document.createElement('select');
        select.id = 'langSelect';
        select.style.border = 'none';
        select.style.background = 'transparent';
        select.style.fontSize = '14px';
        select.style.cursor = 'pointer';
        select.style.outline = 'none';
        select.style.fontWeight = 'bold';

        const optFr = document.createElement('option');
        optFr.value = 'fr';
        optFr.textContent = '🇫🇷 FR';

        const optEn = document.createElement('option');
        optEn.value = 'en';
        optEn.textContent = '🇺🇸 EN';

        select.appendChild(optFr);
        select.appendChild(optEn);
        container.appendChild(select);
        navLinks.appendChild(container);

        select.value = getCurrentLanguage();
        select.addEventListener('change', (e) => {
            setLanguage(e.target.value);
        });
    }
}

// Run translation and setup on DOM load
document.addEventListener('DOMContentLoaded', () => {
    injectLanguageSelector();
    translatePage();
});
