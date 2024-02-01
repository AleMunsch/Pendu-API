import flask
import sqlite3
import random

app = flask.Flask(__name__,template_folder='Views')

#Connection à la bdd
connection = sqlite3.connect('data.db')

#Creation de la table Joueur si innexistante
cursor = connection.cursor()
cursor.execute('Create table if not exists players (id_player integer primary key, pseudo varchar(50), mdp varchar(50), win INT, lose INT)')
connection.commit()
connection.close()

#Def de la route home
@app.route('/')
def home():
    return flask.render_template('inscription.html')

#Ajout du joueur dans la bdd
@app.route('/register', methods=['GET', 'POST'])
def register():
    if flask.request.method == 'POST':
        pseudo = flask.request.values.get('pseudo')
        mdp = flask.request.values.get('mdp')
        
        #On verifie si le pseudo existe déjà
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        cursor.execute('select count(*) from players where pseudo=?',(pseudo,))
        pseudo_existant = cursor.fetchone()[0] > 0
        connection.close()
        if pseudo_existant:
            return flask.render_template('error_page.html', message="Erreur! Ce pseudo est déjà pris !")
        else:
            #On ajoute le nouveau player dans la bdd après verification
            connection = sqlite3.connect('data.db')
            cursor = connection.cursor()
            cursor.execute('INSERT INTO players (pseudo, mdp) VALUES (?,?)', (pseudo, mdp))
            connection.commit()
            connection.close()
            return flask.redirect('/select')
    else:
        return flask.render_template('inscription.html')
    
#Connexion a un compte dejà existant
app.secret_key = 'secret-key'
@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        pseudo = flask.request.form['pseudo']
        mdp = flask.request.form['mdp']
        
        connection =sqlite3.connect('data.db')
        
        cursor = connection.cursor()
        cursor.execute('select id_player from players where pseudo=? and mdp=?',(pseudo,mdp))
        tuple_id_player = cursor.fetchone()
        connection.close()
        
        if tuple_id_player is not None:
            id_player = tuple_id_player[0]
            flask.session['player_id'] = id_player
            flask.session['pseudo'] = pseudo
            return flask.redirect('/select')
        else:
            return flask.render_template('error_page.html', message="Erreur! Le pseudo ou le mot de passe est incorrect !")
    else:
        return flask.render_template('connexion.html')
    
#Def de la route et des niveau de difficultés
@app.route('/select', methods= ['POST' , 'GET'])
def select():
    #Connection à la bdd
    #Creation de la table wwd (words with difficulty) temporaire
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    cursor.execute('Create table if not exists wwd (id_word integer primary key, value text, groupe INTEGER)')
    connection.commit()
    if flask.request.method == 'POST':
        #On récupère les values des submit button de la page selection.html 
        if flask.request.form['buton_select'] == 'Facile':
            difficulté_choisi = 'Facile'
            cursor.execute('INSERT INTO wwd (id_word, value, groupe) SELECT id, value, groupe FROM words WHERE groupe = 1')
            connection.commit()
            connection.close()
            
        elif flask.request.form['buton_select'] == 'Normal':
            difficulté_choisi = 'Normal'
            cursor.execute('INSERT INTO wwd (id_word, value, groupe) SELECT id, value, groupe FROM words WHERE groupe = 2')
            connection.commit()
            connection.close()
            
        elif flask.request.form['buton_select'] == 'Difficile':
            difficulté_choisi = 'Difficile'
            cursor.execute('INSERT INTO wwd (id_word, value, groupe) SELECT id, value, groupe FROM words WHERE groupe = 3')
            connection.commit()
            connection.close()
        print(difficulté_choisi)
        return flask.redirect('/pendu')
    else:
        return flask.render_template('selection.html')

#Fonction initialistaion du jeu     
def game_init():
    connection =sqlite3.connect('data.db')
    cursor = connection.cursor()
    cursor.execute("SELECT value FROM wwd")
    words = cursor.fetchall()
    #Vérification de si il y a des mots présents dans la table wwd
    if not words:
        raise ValueError("Aucun mot trouvé!")
    #Sélection d'un mot random
    select_word = random.choice(words)[0].upper()
    guess_word = ['_'] * len(select_word)
    incorrect_guess = []
    tentatives = 8
    
    connection.close()
    return {
        'select_word': select_word,
        'guess_word': guess_word,
        'incorrect_guess': incorrect_guess,
        'tentatives': tentatives
    }
    
#Fonction score
def score(id_joueur, a_gagne):
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    if a_gagne:
        cursor.execute('UPDATE players SET win = win + 1 WHERE id_player = ?', (id_joueur,))
    else:
        cursor.execute('UPDATE players SET lose = lose + 1 WHERE id_player = ?', (id_joueur,))
    connection.commit()
    connection.close()
    
#Jeu du pendu    
@app.route('/pendu', methods =['GET', 'POST'])
def pendu():
    if flask.request.method == 'GET':
        #Initalisation du jeu
        jeu = game_init()
        flask.session['jeu']= jeu
        return flask.render_template('pendu.html',jeu=jeu)
    elif flask.request.method == 'POST':
        # gestion des guess
        guess = flask.request.form['guess_button'].upper()
        jeu = flask.session.get('jeu')
        
    if guess not in jeu['incorrect_guess'] and guess not in jeu['select_word']:
        jeu['incorrect_guess'].append(guess)
        jeu['tentatives'] -= 1
    else:
        for i in range(len(jeu['select_word'])):
            if jeu['select_word'][i] == guess:
                jeu['guess_word'][i] = guess
                
    
    
    
        
        #Affichage des differents case du pendu
    if jeu['tentatives'] == 8:
        flask.session['jeu'] = jeu
        pendu="""
                 
                 
                 
                 
                 
                 
 ===============
                """
        return flask.render_template('pendu.html', jeu=jeu, word=jeu['guess_word'], tentatives=jeu['tentatives'], pendu=pendu)
    elif jeu['tentatives'] == 7:
        flask.session['jeu'] = jeu
        pendu="""
                
  ||            
  ||            
  ||            
  ||            
  ||            
 ===============
                """
        return flask.render_template('pendu.html', jeu=jeu, word=jeu['guess_word'], tentatives=jeu['tentatives'], pendu=pendu)
    elif jeu['tentatives'] == 6:
        flask.session['jeu'] = jeu
        pendu="""
  ==========Y=  
  ||/           
  ||            
  ||            
  ||            
  ||            
 ===============
                """
        return flask.render_template('pendu.html', jeu=jeu, word=jeu['guess_word'], tentatives=jeu['tentatives'], pendu=pendu)
    elif jeu['tentatives'] == 5:
        flask.session['jeu'] = jeu
        pendu="""
  ==========Y=  
  ||/       |   
  ||        0   
  ||            
  ||            
  ||            
 ===============
                """
        return flask.render_template('pendu.html', jeu=jeu, word=jeu['guess_word'], tentatives=jeu['tentatives'], pendu=pendu)
    elif jeu['tentatives'] == 4:
        flask.session['jeu'] = jeu
        pendu="""
  ==========Y=  
  ||/       |   
  ||        0   
  ||        |   
  ||            
  ||            
 ===============
                """
        return flask.render_template('pendu.html', jeu=jeu, word=jeu['guess_word'], tentatives=jeu['tentatives'], pendu=pendu)
    elif jeu['tentatives'] == 3:
        flask.session['jeu'] = jeu
        pendu="""
  ==========Y=  
  ||/       |   
  ||        0   
  ||       /|   
  ||            
  ||            
 ===============
                """
        return flask.render_template('pendu.html', jeu=jeu, word=jeu['guess_word'], tentatives=jeu['tentatives'], pendu=pendu)
    elif jeu['tentatives'] == 2:
        flask.session['jeu'] = jeu
        pendu="""
  ==========Y=  
  ||/       |   
  ||        0   
  ||       /|'\'  
  ||            
  ||            
 ===============
                """
        return flask.render_template('pendu.html', jeu=jeu, word=jeu['guess_word'], tentatives=jeu['tentatives'], pendu=pendu)
    elif jeu['tentatives'] == 1:
        flask.session['jeu'] = jeu
        pendu="""
  ==========Y=  
  ||/       |   
  ||        0   
  ||       /|'\'  
  ||       /    
  ||            
 ===============
                """
        return flask.render_template('pendu.html', jeu=jeu, word=jeu['guess_word'], tentatives=jeu['tentatives'], pendu=pendu)
    elif jeu['tentatives'] == 0:
        flask.session['jeu'] = jeu
        #Si le joueur a perdu
        score(flask.session['player_id'], False)
        #On drop la table wwd
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        cursor.execute('drop table wwd')
        connection.commit()
        connection.close()
        pendu="""
  ==========Y=  
  ||/       |   
  ||        0   
  ||       /|'\'  
  ||       /|   
  ||            
 ===============
                """
        return flask.render_template('pendu.html', jeu=jeu, word=jeu['guess_word'], tentatives=jeu['tentatives'], pendu=pendu, word_select=jeu['select_word'], result="Dommage ! C'est perdu, le mot à deviné était :")
    elif all(char != '_' for char in guess):
        #Si le joueur a gagné
        score(flask.session['player_id'], True)
        #On drop la table wwd
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        cursor.execute('drop table wwd')
        connection.commit()
        connection.close()
        flask.session['jeu'] = jeu
        print('1')
        return flask.render_template('pendu.html', jeu=jeu, word=jeu['guess_word'], tentatives=jeu['tentatives'], pendu=pendu, word_select=jeu['select_word'], result="Bravo ! C'est gagné ! Le mot à deviné était :")
    else:
        print('2')
        flask.session['jeu'] = jeu

#Run l'app
app.run(port=8888)