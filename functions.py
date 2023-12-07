import sqlite3
from flask import session, redirect, render_template
from functools import wraps

from werkzeug.security import generate_password_hash

db_locale = "database.db"
connie = sqlite3.connect(db_locale, check_same_thread=False)
connie.row_factory = sqlite3.Row
c = connie.cursor()



def create_users_table():
    c.execute('''
    CREATE TABLE IF NOT EXISTS users
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    age INTEGER,
    gender TEXT,
    level TEXT,
    mix_level,
    mail TEXT,
    hash TEXT
    )''') 

    connie.commit()


def insert_user(username, first_name, last_name, age, gender, level, mix_level, password, mail):
    
    # Generate passsword hash
    hash = generate_password_hash(password)

    c.execute('''INSERT INTO users (username, first_name, last_name, age, gender, level, mix_level, hash, mail) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
    (username, first_name, last_name, age, gender, level, mix_level, hash, mail))

    connie.commit()

def get_users():

    users = c.execute(''' SELECT username FROM users ''').fetchall()

    users = list(map(lambda x: x["username"], users))
    
    return users

def create_tournaments_table():
    c.execute('''
    CREATE TABLE IF NOT EXISTS tournaments
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    club TEXT,
    level TEXT,
    gender TEXT,
    tournament_date DATETIME,
    subscription_date DATETIME,
    n_players INTEGER,
    maximum_slots TEXT,
    description TEXT
    )''')

    connie.commit()


def insert_tournament(user, club, level, gender, tournament_date, subscription_date, n_players, maximum_slots, description):
    
    c.execute(''' INSERT INTO tournaments (user, club, level, gender, tournament_date, subscription_date, n_players, maximum_slots, description) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
    (user, club, level, gender, tournament_date, subscription_date, n_players, maximum_slots, description))

    connie.commit()

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def create_users_tournaments_table():
    c.execute('''
    CREATE TABLE IF NOT EXISTS users_tournaments
    (player_id INTEGER,
    player_username TEXT,
    partner_id INTEGER,
    partner_username TEXT,
    tournament_id INTEGER,
    subscripted TEXT,
    FOREIGN KEY(player_id) REFERENCES user(id),
    FOREIGN KEY(tournament_id) REFERENCES tournaments(id)
    )''')


def users_subscription(id, player_username, partner_id, partner_username, tournament_id, subscripted):
    c.execute('''INSERT INTO users_tournaments (player_id, player_username, partner_id, partner_username, tournament_id, subscripted) VALUES (?, ?, ?, ?, ?, ?)''', 
            (id, player_username, partner_id, partner_username, tournament_id, subscripted))

    connie.commit()


def subscribed(tournament_id):

    users = c.execute('''SELECT * FROM users WHERE id IN (SELECT player_id FROM users_tournaments WHERE tournament_id = ?) 
                     OR id IN (SELECT partner_id FROM users_tournaments WHERE tournament_id = ?) ''', (tournament_id, tournament_id)).fetchall()

    users = list(map(lambda x: x["username"], users))

    return users

def deregister_players(player_username):

    c.execute('''DELETE FROM users_tournaments WHERE player_username = ?''', [player_username]) 
    c.execute('''DELETE FROM users_tournaments WHERE partner_username = ?''', [player_username])

    connie.commit()

def delete_tournament(tournament_id):

    c.execute('''DELETE FROM tournaments WHERE id = ?''', [tournament_id]) 

    connie.commit()


