import sqlite3

# Connexion à la base de données SQLite (créez-la si elle n'existe pas)
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# Création de la table 'words' si elle n'existe pas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        value TEXT NOT NULL,
        groupe INTEGER
    )
''')
conn.commit()

# Fonction pour insérer une liste de mots depuis un fichier
def insert_words_from_file(file_path):
    try:
        with open("words.txt", 'r') as file:
            words_list = [line.strip() for line in file.readlines()]

        # Insérer les mots dans la table 'words'
        for word_value in words_list:
            cursor.execute('INSERT INTO words (value) VALUES (?)', (word_value,))
        
        conn.commit()
        cursor.execute('UPDATE words SET groupe = 1 WHERE LENGTH(value) BETWEEN 3 AND 4')
        conn.commit()

        cursor.execute('UPDATE words SET groupe = 2 WHERE LENGTH(value) BETWEEN 5 AND 6')
        conn.commit()

        cursor.execute('UPDATE words SET groupe = 3 WHERE LENGTH(value) >= 7')
        conn.commit()

        print("Liste de mots insérée avec succès.")
    
    except Exception as e:
        print(f"Erreur lors de l'insertion des mots : {e}")

# Remplacez 'fichier.txt' par le chemin de votre fichier
insert_words_from_file('words.txt')
# Fermer la connexion à la base de données
conn.close()
