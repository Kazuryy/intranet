-- ============================================================
-- Création de la base de données
-- ============================================================
CREATE DATABASE IF NOT EXISTS guardia_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE guardia_db;

-- ============================================================
-- Bâtiment
-- ============================================================
CREATE TABLE Batiment (
    ID   INT AUTO_INCREMENT PRIMARY KEY,
    Nom  VARCHAR(50) NOT NULL
);

-- ============================================================
-- Étage
-- ============================================================
CREATE TABLE Etage (
    ID           INT AUTO_INCREMENT PRIMARY KEY,
    Numero       INT NOT NULL,
    ID_Batiment  INT NOT NULL,
    FOREIGN KEY (ID_Batiment) REFERENCES Batiment(ID) ON DELETE CASCADE
);

-- ============================================================
-- Salle
-- ============================================================
CREATE TABLE Salle (
    ID       INT AUTO_INCREMENT PRIMARY KEY,
    Nom      VARCHAR(100) NOT NULL,
    ID_Etage INT NOT NULL,
    FOREIGN KEY (ID_Etage) REFERENCES Etage(ID) ON DELETE CASCADE
);

-- ============================================================
-- User
-- ============================================================
CREATE TABLE User (
    ID           INT AUTO_INCREMENT PRIMARY KEY,
    Type         ENUM('élève', 'employé', 'parent', 'administrateur') NOT NULL,
    Nom          VARCHAR(100) NOT NULL,
    Prenom       VARCHAR(100) NOT NULL,
    Username     VARCHAR(100) NOT NULL UNIQUE,
    Password     VARCHAR(255) NOT NULL,
    Mail_Interne VARCHAR(150) UNIQUE,
    Is_Active           BOOLEAN NOT NULL DEFAULT TRUE,
    Setup_Token         VARCHAR(100) UNIQUE,
    Setup_Token_Expires DATETIME
);

-- ============================================================
-- Information
-- ============================================================
CREATE TABLE Information (
    ID      INT AUTO_INCREMENT PRIMARY KEY,
    ID_User INT NOT NULL,
    Numero  VARCHAR(15),
    Mail    VARCHAR(150),
    Adresse VARCHAR(255),
    FOREIGN KEY (ID_User) REFERENCES User(ID) ON DELETE CASCADE
);

-- ============================================================
-- Direction
-- ============================================================
CREATE TABLE Direction (
    ID      INT AUTO_INCREMENT PRIMARY KEY,
    ID_User INT NOT NULL,
    Role    VARCHAR(100),
    FOREIGN KEY (ID_User) REFERENCES User(ID) ON DELETE CASCADE
);

-- ============================================================
-- Matière
-- ============================================================
CREATE TABLE Matiere (
    ID  INT AUTO_INCREMENT PRIMARY KEY,
    Nom VARCHAR(100) NOT NULL
);

-- ============================================================
-- Prof
-- ============================================================
CREATE TABLE Prof (
    ID         INT AUTO_INCREMENT PRIMARY KEY,
    ID_User    INT NOT NULL,
    ID_Matiere INT NOT NULL,
    FOREIGN KEY (ID_User)    REFERENCES User(ID)    ON DELETE CASCADE,
    FOREIGN KEY (ID_Matiere) REFERENCES Matiere(ID) ON DELETE RESTRICT
);

-- ============================================================
-- Classe
-- ============================================================
CREATE TABLE Classe (
    ID                INT AUTO_INCREMENT PRIMARY KEY,
    Niveau            INT NOT NULL,
    Suffixe           VARCHAR(10),
    ID_Prof_Principal INT,
    Annee             YEAR NOT NULL,
    FOREIGN KEY (ID_Prof_Principal) REFERENCES Prof(ID) ON DELETE SET NULL
);

-- ============================================================
-- Élève (ID_Responsable ajouté après Parent)
-- ============================================================
CREATE TABLE Eleve (
    ID             INT AUTO_INCREMENT PRIMARY KEY,
    ID_User        INT NOT NULL,
    ID_Classe      INT,
    ID_Responsable INT,
    Groupe         VARCHAR(1),
    Date_Naissance DATE,
    FOREIGN KEY (ID_User)   REFERENCES User(ID)   ON DELETE CASCADE,
    FOREIGN KEY (ID_Classe) REFERENCES Classe(ID) ON DELETE RESTRICT
);

-- ============================================================
-- Parent
-- ============================================================
CREATE TABLE Parent (
    ID             INT AUTO_INCREMENT PRIMARY KEY,
    ID_User        INT NOT NULL,
    ID_Eleve       INT NOT NULL,
    ID_Information INT,
    FOREIGN KEY (ID_User)        REFERENCES User(ID)        ON DELETE CASCADE,
    FOREIGN KEY (ID_Eleve)       REFERENCES Eleve(ID)       ON DELETE CASCADE,
    FOREIGN KEY (ID_Information) REFERENCES Information(ID) ON DELETE SET NULL
);

-- Résolution de la dépendance circulaire Élève <-> Parent
ALTER TABLE Eleve
    ADD CONSTRAINT fk_eleve_responsable
    FOREIGN KEY (ID_Responsable) REFERENCES Parent(ID) ON DELETE SET NULL;

-- ============================================================
-- Employé
-- ============================================================
CREATE TABLE Employe (
    ID      INT AUTO_INCREMENT PRIMARY KEY,
    ID_User INT NOT NULL,
    Role    VARCHAR(100),
    FOREIGN KEY (ID_User) REFERENCES User(ID) ON DELETE CASCADE
);

-- ============================================================
-- Évènement
-- ============================================================
CREATE TABLE Evenement (
    ID          INT AUTO_INCREMENT PRIMARY KEY,
    Type        VARCHAR(100) NOT NULL,
    Nom         VARCHAR(150) NOT NULL,
    Responsable VARCHAR(150),
    Date        DATETIME NOT NULL,
    Invites     TEXT
);

-- ============================================================
-- Menu
-- ============================================================
CREATE TABLE Menu (
    ID           INT AUTO_INCREMENT PRIMARY KEY,
    Date         DATETIME NOT NULL,
    Entree       VARCHAR(150),
    Plat         VARCHAR(150),
    Dessert      VARCHAR(150),
    Special      BOOLEAN DEFAULT FALSE,
    Special_Info VARCHAR(255),
    ID_Evenement INT,
    FOREIGN KEY (ID_Evenement) REFERENCES Evenement(ID) ON DELETE SET NULL
);

-- ============================================================
-- Cours
-- ============================================================
CREATE TABLE Cours (
    ID         INT AUTO_INCREMENT PRIMARY KEY,
    ID_Matiere INT NOT NULL,
    ID_Prof    INT NOT NULL,
    ID_Classe  INT NOT NULL,
    Debut      DATETIME NOT NULL,
    Fin        DATETIME NOT NULL,
    Etat       ENUM('planifié', 'en cours', 'terminé', 'annulé') NOT NULL DEFAULT 'planifié',
    ID_Salle   INT,
    FOREIGN KEY (ID_Matiere) REFERENCES Matiere(ID) ON DELETE RESTRICT,
    FOREIGN KEY (ID_Prof)    REFERENCES Prof(ID)    ON DELETE RESTRICT,
    FOREIGN KEY (ID_Classe)  REFERENCES Classe(ID)  ON DELETE CASCADE,
    FOREIGN KEY (ID_Salle)   REFERENCES Salle(ID)   ON DELETE SET NULL
);

-- ============================================================
-- Devoir
-- ============================================================
CREATE TABLE Devoir (
    ID          INT AUTO_INCREMENT PRIMARY KEY,
    ID_Classe   INT NOT NULL,
    ID_Matiere  INT NOT NULL,
    Type        ENUM('exercice', 'soutenance', 'exposé', 'contrôle', 'autre') NOT NULL,
    Date_Limite DATETIME NOT NULL,
    Consigne    TEXT,
    ID_Prof     INT NOT NULL,
    FOREIGN KEY (ID_Classe)  REFERENCES Classe(ID)  ON DELETE CASCADE,
    FOREIGN KEY (ID_Matiere) REFERENCES Matiere(ID) ON DELETE RESTRICT,
    FOREIGN KEY (ID_Prof)    REFERENCES Prof(ID)    ON DELETE RESTRICT
);

-- ============================================================
-- Devoir_Status
-- ============================================================
CREATE TABLE Devoir_Status (
    ID        INT AUTO_INCREMENT PRIMARY KEY,
    ID_Devoir INT NOT NULL,
    ID_Eleve  INT NOT NULL,
    Status    BOOLEAN DEFAULT FALSE,
    Fichier   VARCHAR(255),
    FOREIGN KEY (ID_Devoir) REFERENCES Devoir(ID) ON DELETE CASCADE,
    FOREIGN KEY (ID_Eleve)  REFERENCES Eleve(ID)  ON DELETE CASCADE
);

-- ============================================================
-- Évaluation
-- ============================================================
CREATE TABLE Evaluation (
    ID          INT AUTO_INCREMENT PRIMARY KEY,
    ID_Eleve    INT NOT NULL,
    ID_Matiere  INT NOT NULL,
    Note        DECIMAL(4,2) NOT NULL,
    Note_Max    DECIMAL(4,2) NOT NULL DEFAULT 20,
    Coefficient INT NOT NULL DEFAULT 1,
    Date        DATETIME NOT NULL,
    FOREIGN KEY (ID_Eleve)   REFERENCES Eleve(ID)   ON DELETE CASCADE,
    FOREIGN KEY (ID_Matiere) REFERENCES Matiere(ID) ON DELETE RESTRICT
);

-- ============================================================
-- Mail
-- ============================================================
CREATE TABLE Mail (
    ID               INT AUTO_INCREMENT PRIMARY KEY,
    ID_Expediteur    INT NOT NULL,
    ID_Destinataire  INT NOT NULL,
    Objet            VARCHAR(255),
    Contenu          TEXT,
    Date             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ID_Expediteur)   REFERENCES User(ID) ON DELETE CASCADE,
    FOREIGN KEY (ID_Destinataire) REFERENCES User(ID) ON DELETE CASCADE
);

-- ============================================================
-- Communication
-- ============================================================
CREATE TABLE Communication (
    ID        INT AUTO_INCREMENT PRIMARY KEY,
    ID_User   INT NOT NULL,
    Cible     ENUM('parent', 'élève', 'prof', 'tous', 'classe') NOT NULL,
    ID_Cible  INT,
    Objet     VARCHAR(255),
    Contenu   TEXT,
    Date_Debut DATETIME,
    Date_Fin   DATETIME,
    FOREIGN KEY (ID_User) REFERENCES User(ID) ON DELETE CASCADE
);

-- ============================================================
-- Log (audit)
-- ============================================================
CREATE TABLE Log (
    ID          INT AUTO_INCREMENT PRIMARY KEY,
    ID_User     INT,
    Action      VARCHAR(100) NOT NULL,
    Target_Type VARCHAR(50),
    Target_ID   INT,
    IP_Address  VARCHAR(45),
    User_Agent  VARCHAR(255),
    Created_At  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ID_User) REFERENCES User(ID) ON DELETE SET NULL
);

-- ============================================================
-- Assiduité
-- ============================================================
CREATE TABLE Assiduite (
    ID             INT AUTO_INCREMENT PRIMARY KEY,
    ID_Eleve       INT NOT NULL,
    ID_Responsable INT NOT NULL,
    Type           ENUM('absent', 'retard', 'présent', 'excusé') NOT NULL,
    Date           DATETIME NOT NULL,
    FOREIGN KEY (ID_Eleve)       REFERENCES Eleve(ID) ON DELETE CASCADE,
    FOREIGN KEY (ID_Responsable) REFERENCES User(ID)  ON DELETE RESTRICT
);