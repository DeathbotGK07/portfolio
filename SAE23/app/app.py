# Import des bibliothèques nécessaires
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os


# Initialisation de l'application Flask
app = Flask(__name__)
app.secret_key = 'secret123'  # Clé secrète pour les sessions et les messages flash


# Configuration de la base de données (PostgreSQL par défaut, variable d’environnement prioritaire)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    "postgresql://postgres:progtr00@db:5432/db"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Désactivation du suivi des modifications


# Initialisation de SQLAlchemy
db = SQLAlchemy(app)


# Configuration de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)  # Initialisation avec l'application Flask
login_manager.login_view = 'login'  # Redirection vers cette vue si l'utilisateur n'est pas connecté


# Modèle utilisateur (hérite de UserMixin pour Flask-Login)
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


# Modèle de compétence
class Competence(db.Model):
    __tablename__ = "competences"
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    niveau = db.Column(db.String(50), nullable=False)
    semestre = db.Column(db.String(10), nullable=False)


# Fonction de chargement d'utilisateur pour Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Route de base : redirection vers le dashboard
@app.route('/')
def home():
    return redirect(url_for('dashboard'))


# Route d'inscription (GET pour afficher, POST pour enregistrer)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])  # Hash du mot de passe
        # Vérification de l'existence de l'utilisateur
        if User.query.filter_by(username=username).first():
            flash("Ce nom d'utilisateur existe déjà.", "warning")
            return redirect(url_for('register'))
        # Création d'un nouvel utilisateur
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        try:
            db.session.commit()
            flash("Inscription réussie. Connectez-vous.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de l'enregistrement : {e}")
            flash("Erreur lors de l'enregistrement.", "danger")
            return redirect(url_for('register'))
    return render_template('register.html')  # Affichage du formulaire


# Route de connexion (GET pour formulaire, POST pour authentification)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        # Vérification du mot de passe haché
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Connexion réussie.", "success")
            return redirect(url_for('dashboard') + '#services')
        else:
            flash("Identifiants invalides.", "danger")
            return redirect(url_for('login'))
    # Si l'utilisateur est déjà connecté, rediriger
    if current_user.is_authenticated:
        return redirect(url_for('dashboard') + '#services')
    return render_template('login.html')


# Route de déconnexion
@app.route('/logout')
def logout():
    logout_user()
    flash("Déconnecté avec succès.", "info")
    return redirect(url_for('dashboard') + '#services')


# Affichage du tableau de bord avec la liste des compétences
@app.route('/dashboard')
def dashboard():
    competences = Competence.query.all()
    return render_template('dashboard.html', competences=competences)


# Ajout d'une compétence (authentification requise)
@app.route('/ajouter_competence', methods=['POST'])
@login_required
def ajouter_competence():
    nom = request.form.get('nom')
    niveau = request.form.get('niveau')
    semestre = request.form.get('semestre')
    # Vérification des champs
    if nom and niveau and semestre:
        comp = Competence(nom=nom, niveau=niveau, semestre=semestre)
        db.session.add(comp)
        try:
            db.session.commit()
            flash("Compétence ajoutée.", "success")
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de l'ajout de compétence : {e}")
            flash("Erreur lors de l'ajout de compétence.", "danger")
    else:
        flash("Tous les champs sont requis.", "warning")
    return redirect(url_for('dashboard') + '#services')


# Suppression d'une compétence (authentification requise)
@app.route('/supprimer_competence/<int:id>')
@login_required
def supprimer_competence(id):
    comp = Competence.query.get_or_404(id)  # 404 si non trouvé
    db.session.delete(comp)
    try:
        db.session.commit()
        flash("Compétence supprimée.", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de la suppression de compétence : {e}")
        flash("Erreur lors de la suppression de compétence.", "danger")
    return redirect(url_for('dashboard') + '#services')


# Lancement de l'application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Création des tables si elles n'existent pas
    app.run(host='0.0.0.0', debug=True)  # Lancement sur tous les hôtes en mode debug
