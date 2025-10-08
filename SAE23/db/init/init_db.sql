-- Création de la table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL
);

-- Création de la table des compétences
CREATE TABLE IF NOT EXISTS competences (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    niveau VARCHAR(50) NOT NULL,
    semestre VARCHAR(10) NOT NULL
);
