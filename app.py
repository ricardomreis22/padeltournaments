from flask import Flask, redirect, render_template, request, session
from werkzeug.security import check_password_hash
from flask_session import Session

from datetime import date
from flask_bootstrap import Bootstrap
from flask_datepicker import datepicker

from functions import *

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

Bootstrap(app)
datepicker(app)

    
@app.route("/", methods=["GET", "POST"])
def homepage():
    if request.method == "POST":
        return "hello"
    else:
        return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    # Initialize table users
    create_users_table()

    if request.method == "POST":
        
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        mail = request.form.get("e-mail")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        age = request.form.get("age")
        gender = request.form.get("gender")
        level = request.form.get("level")
        mix_level = request.form.get("mix_level")
        error = ""

        users = get_users()


        # Ensure username was submitted
        if not username or not password or not confirmation or not mail or not age or not gender or not level or not mix_level:
            error = " All fields are required!"
        
        # Ensure password and password confirmation are the same
        elif password != confirmation:
            error = "Password and does not match!"
   
        # Ensure the username isnt taken already
        elif username in users:
            error = f"Username {username} already exists!"

        # Ensure the age is between 16 and 99
        elif int(age) < 16 or int(age) > 99:
            error = "You cannot register yourself"

        # Ensure gender is male or female
        elif gender != "male" and gender != "female":
            error = "Gender must be male or female!"

        # Ensure level in 1 to 5       
        elif level not in ["1", "2", "3", "4", "5"] :
            error = "You have to register in a level"

        # Ensure mix level in 1 to 3
        elif mix_level not in ["1", "2", "3","4", "5"]:
            error = "You have to register in one of these mix levels"
        
        if error == "":
            # Insert new user and hash into SQL table
            insert_user(username, first_name, last_name, age, gender, level, mix_level, password, mail) 
            # Redirect user to home page
            return redirect("/")  
        
        else:
            return render_template("register.html", first_name = first_name, last_name = last_name, mail = mail, 
            age = age, gender = gender, level = level, mix_level = mix_level, username = username, error = error)


    else:
        return render_template("register.html") 

@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # Initialize tournaments and user_tournaments table
    create_tournaments_table()
    create_users_tournaments_table()

    # Get username and password
    username = request.form.get("username")
    password = request.form.get("password")

    # Get all users already registered
    users = get_users()

    error= ""
        
    # User reached route via GET
    if request.method == "GET":
        return render_template("login.html")

    # User reached route via POST (as by submitting a form via POST)
    else:
        
        # Ensure username was submitted
        if not username:
            error = "Must provide username!"
            return render_template("login.html", error = error)

        # Get user hash
        user_hash = c.execute('''SELECT hash FROM users WHERE username = ?''', [username]).fetchone()[0]

        # Ensure password was submitted
        if not password:
            error = "Must provide password!"

        # Ensure username exists and password is correct
        elif not username in users:
            error = "Username is not correct!"

        elif check_password_hash(user_hash, password) == False:
            error = "Password is not correct!"

        if error == "":
            # Remember which user has logged in
            session["username"] = username

            # Redirect user to home page
            return redirect("/user")
        else: 
            return render_template("login.html", error = error)

@app.route("/user", methods=["GET", "POST"])
def user():
    if request.method == "GET":
        
        # Get username from session
        username = session["username"]

        # Get information of that username
        information = c.execute(''' SELECT * FROM users WHERE username = ?''', [username]).fetchone()

        # Present user information
        return render_template("user.html", information = information)

@app.route("/update_user", methods=["GET","POST"])
def update_user():
    # Get session username and information
    username = session["username"]
    information = c.execute(''' SELECT * FROM users WHERE username = ?''', [username]).fetchone()
    id = c.execute(''' SELECT * FROM users WHERE username = ?''', [username]).fetchone()[0]
    gender = c.execute(''' SELECT gender FROM users WHERE username = ?''', [username]).fetchone()[0]
    level = c.execute(''' SELECT level FROM users WHERE username = ?''', [username]).fetchone()[0]
    mix_level = c.execute(''' SELECT mix_level FROM users WHERE username = ?''', [username]).fetchone()[0]
    
    if request.method == "GET":

        return render_template ("update_user.html", information=information, gender = gender, level=level, mix_level = mix_level)

    else:
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        mail = request.form.get("mail")
        age = request.form.get("age")
        gender = request.form.get("gender")
        level = request.form.get("level")
        mix_level = request.form.get("mix_level")
        error = ""
        

        # Ensure gender is male or female
        if gender != "male" and gender != "female":
            error = "Gender must be male or female!"
            
        elif not age or not first_name or not last_name:
            error = " Information are missing!"

        # Ensure the age is between 16 and 99
        elif int(age) < 16 or int(age) > 99:
            error = "You cannot register yourself!"

        # Ensure level in 1 to 5       
        elif level not in ["1", "2", "3", "4", "5"] :
            error = "You have to register in a level!"

        # Ensure mix level in 1 to 3
        elif mix_level not in ["1", "2", "3","4", "5"]:
            error = "You have to register in one of these mix levels!"
        
        if error == "":        
            
            # Update user information
            c.execute('''UPDATE users SET first_name = ?, last_name = ?, mail = ?, age = ?, gender = ?, level = ?, mix_level = ? WHERE id = ?''', 
                    (first_name, last_name, mail, age, gender, level, mix_level, id))         
                    
            connie.commit()

            # Redirect user to home page
            return redirect("/user")  
        
        else:

            return render_template("update_user.html", information = information, first_name = first_name, last_name = last_name, mail = mail, 
            age = age, gender = gender, level = level, mix_level = mix_level, username = username, error = error)
          
@app.route("/change_password", methods=["GET","POST"])
def change_password():  
    username = session["username"]

    if request.method == "GET":

        return render_template ("change_password.html")

    else:
        password = request.form.get("password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")
        user_hash = c.execute('''SELECT hash FROM users WHERE username = ?''', [username]).fetchone()[0]
        error = ""
        
        # Ensure password was submitted
        if not password:
            error = "Must provide password!"
        # Ensure new password was submitted
        elif not new_password:
            error = "Must provide new password!"

        # Ensure confirmation was submitted
        elif not confirmation:
            error = "Must repeat your password!"

        # Verify old password is correct
        elif check_password_hash(user_hash, password) == False:
            error = "Your old password is not correct!"
        
        elif new_password != confirmation:
            error = "Confirmation must be equal to new password!"

        if error == "":
            hash = generate_password_hash(new_password)

            # Update new password
            c.execute('''UPDATE users SET hash = ? WHERE username = ?''', (hash, username)) 

            connie.commit()
            
            return redirect("/user")

        else:
            return render_template("change_password.html", error = error)            

    
@app.route("/new_tournament", methods=["GET", "POST"])
def new_tournament():
    
    user = session["username"]
    club = request.form.get("club")
    level= request.form.get("level")
    gender= request.form.get("gender")
    tournament_date= request.form.get("tournament_start")
    subscription_date = request.form.get("subscription")
    description = request.form.get("description")
    maximum_slots = request.form.get("slots")
    n_players = 0
    error = ""

    if request.method == "GET":

        return render_template("new_tournament.html")

    else:
                    
        today = str(date.today())

        if today > tournament_date:
            error = "The tournament must be after today!"
        
        if subscription_date > tournament_date or subscription_date == tournament_date:
            error = "Subscription date must be before the tournament date!"
        
        if not club or not level or not gender or not tournament_date or not subscription_date or not description or not maximum_slots:
            
            error = "Information missing!" 

        if error == "":

                        
            insert_tournament(user, club, level, gender, tournament_date, subscription_date, n_players, maximum_slots, description)

            return redirect("/tournaments")

        else: 
            return render_template("new_tournament.html",today = today, club=club, level = level, gender = gender, tournament_date = tournament_date, subscription_date = subscription_date,
            description = description, maximum_slots = maximum_slots, n_players = n_players, error = error)


@app.route("/tournaments", methods=["GET", "POST"])
def tournaments():
    
    username = session["username"]

    if request.method == "GET":

        # Selecionar os torneios que estão inseridos
        tournaments = c.execute(''' SELECT * FROM tournaments''').fetchall()
             
        return render_template("tournaments.html", username = username, tournaments=tournaments)
    
    if request.method == "POST":
        
        # Selecionar os torneios que estão inseridos
        tournaments = c.execute(''' SELECT * FROM tournaments''').fetchall()
        
        return render_template("tournaments.html", username = username, tournaments=tournaments)



@app.route("/tournament/<tournament_id>", methods=["GET", "POST"])
def info(tournament_id):

    # Select tournament
    tournament = c.execute(''' SELECT * FROM tournaments WHERE id = ?''',[tournament_id]).fetchone()
    # Quantos users já estão inscritos em cada torneio
    total_players = c.execute(''' SELECT COUNT(player_id) FROM users_tournaments WHERE tournament_id = ?''', [tournament_id]).fetchone()[0] * 2
   
    # Quantas o numero maximo de vagas deste torneio
    maximum_slots = int(c.execute(''' SELECT maximum_slots FROM tournaments WHERE id = ?''',[tournament_id]).fetchone()[0])

    # Check users already subscribed
    subscribed_users = subscribed(tournament_id) 
    
    player_username = session["username"]

    error = ""

    subscribed_players = c.execute(''' SELECT * FROM users_tournaments WHERE tournament_id = ?''', [tournament_id]).fetchall()        
    
    # Players subscribed in this tournament
    players = c.execute(''' SELECT player_username FROM users_tournaments WHERE tournament_id = ?''', [tournament_id]).fetchall()
    
    # Partners subscribed in this tournament
    partners = c.execute(''' SELECT partner_username FROM users_tournaments WHERE tournament_id = ?''', [tournament_id]).fetchall()
    
    # List of all the players subscribed in this tournament
    all_players = list(map(lambda x:x[0], players)) + list(map(lambda x:x[0], partners))
    
    # check if user is subscribed in this tournament
    is_enrolled = session["username"] in all_players

    subscription_date = c.execute(''' SELECT subscription_date FROM tournaments WHERE id = ?''',[tournament_id]).fetchone()[0]

    today = str(date.today())


    if request.method == "GET":

        return render_template("tournament.html", tournament = tournament, subscribed_players = subscribed_players,
        total_players = total_players, maximum_slots = maximum_slots, is_enrolled = is_enrolled)

            
    else:

        player_username = request.form.get("username")

        partner_username = request.form.get("teammate_username")

        # Select all users

        users = get_users()

        # Check if username registered is the session username
        if player_username != session["username"]:
            error = "That is not your username!"

        # check if teammate_username exists and is not session username
        elif not partner_username in users:
            error = "Teammate username doesnt exist!"

        elif partner_username == session["username"]:
            error = "Your username and yours teammate username must be differente"

        # If players already registered cant register again
        elif player_username in subscribed_users:
            error = "User already registered in this tournament"

        elif partner_username in subscribed_users:
            error = "Teammate already registered in this tournament"
        
        elif today > subscription_date:
            error = "The deadline to subscribe in this tournament its over!"

        if error == "":

            # Select player and partner genders and levels
            player_gender = c.execute(''' SELECT gender FROM users WHERE username = ?''',[player_username]).fetchone()[0]
            partner_gender = c.execute(''' SELECT gender FROM users WHERE username = ?''',[partner_username]).fetchone()[0]
            player_level = c.execute(''' SELECT level FROM users WHERE username = ?''',[player_username]).fetchone()[0]
            partner_level = c.execute(''' SELECT level FROM users WHERE username = ?''',[partner_username]).fetchone()[0]
            player_mix_level = c.execute(''' SELECT mix_level FROM users WHERE username = ?''',[partner_username]).fetchone()[0]
            partner_mix_level = c.execute(''' SELECT mix_level FROM users WHERE username = ?''',[partner_username]).fetchone()[0]

            # Select tournament level and gender
            tournament_level = c.execute(''' SELECT level FROM tournaments WHERE id = ?''',[tournament_id]).fetchone()[0]
            tournament_gender = c.execute(''' SELECT gender FROM tournaments WHERE id = ?''',[tournament_id]).fetchone()[0]


            # Verify that only players of tournament level and gender can register in that tournament
            if tournament_gender == "male" or tournament_gender == "female":
                if player_gender != tournament_gender:
                    error = "You cant register in this tournament!"
                if partner_gender != tournament_gender:
                    error = "Your teammate cant register in this tournament!"
                if player_level != tournament_level or partner_level != tournament_level:
                    error =  "You cant register in this tournament!"
                if partner_level != tournament_level:
                    error = "Your teammate cant register in this tournament!"
            elif tournament_gender == "mix":
                if player_gender == partner_gender:
                    error = "You cant register with teammate of same gender!"
                if player_mix_level != tournament_level or partner_mix_level != tournament_level:
                    error = " You cant register in this tournament!"
            
            if error == "":
                # Select id of sesion username and his partner
                id = c.execute(''' SELECT id FROM users WHERE username = ?''',[player_username]).fetchone()[0]
                partner_id = c.execute(''' SELECT id FROM users WHERE username = ?''',[partner_username]).fetchone()[0]

                # Number of players registered in tournament
                n_players = c.execute(''' SELECT n_players FROM tournaments WHERE id = ?''',[tournament_id]).fetchone()[0]

                subscripted = "YES"

                # Register in tournament user and partner
                users_subscription(id, player_username, partner_id, partner_username, tournament_id, subscripted) 

                # Increase number of players subscribed
                n_players = n_players + 2
                c.execute('''UPDATE tournaments SET n_players = ? WHERE id = ?''',(n_players, tournament_id))
                connie.commit()
            
                # Select players registered in the tournament
                subscribed_players = c.execute(''' SELECT * FROM users_tournaments WHERE tournament_id = ?''', [tournament_id]).fetchall()

                return redirect("/tournament/" + tournament_id)
                    
            else:
                return render_template("tournament.html", tournament = tournament, subscribed_players = subscribed_players,
        total_players = total_players, maximum_slots = maximum_slots, is_enrolled = is_enrolled, error = error)

        else:
            return render_template("tournament.html", tournament = tournament, subscribed_players = subscribed_players,
        total_players = total_players, maximum_slots = maximum_slots, is_enrolled = is_enrolled, error = error)

@app.route("/tournament/<tournament_id>/delete", methods=["GET"])
def delete(tournament_id):
    tournaments = c.execute(''' SELECT * FROM tournaments''').fetchall()
    error = ""
    username = session["username"]
    user = c.execute(''' SELECT user FROM tournaments WHERE id = ?''',[tournament_id]).fetchone()[0]
    if username != user:
        error = "Only the user that created the tournament can delete them!"
        
    if error == "":
        delete_tournament(tournament_id)
        return redirect("/tournaments")
    else:
        return render_template("tournaments.html", error=error, tournaments=tournaments)
    



@app.route("/tournament/<tournament_id>/update", methods=["GET","POST"])
def update(tournament_id):
    
    # Select tournament 
    tournaments = c.execute(''' SELECT * FROM tournaments ''').fetchall()
    tournament = c.execute(''' SELECT * FROM tournaments WHERE id = ?''',[tournament_id]).fetchone()
    club = c.execute(''' SELECT club FROM tournaments WHERE id = ?''', [tournament_id]).fetchone()[0]
    level = c.execute(''' SELECT level FROM tournaments WHERE id = ?''', [tournament_id]).fetchone()[0]
    gender = c.execute(''' SELECT gender FROM tournaments WHERE id = ?''', [tournament_id]).fetchone()[0]
    tournament_date= c.execute(''' SELECT tournament_date FROM tournaments WHERE id = ?''', [tournament_id]).fetchone()[0]
    subscription_date = c.execute(''' SELECT subscription_date FROM tournaments WHERE id = ?''', [tournament_id]).fetchone()[0]
    description = c.execute(''' SELECT description FROM tournaments WHERE id = ?''', [tournament_id]).fetchone()[0]
    maximum_slots = request.form.get("slots")
    error = ""

    if request.method == "GET":

        error = ""

        # Quantos users já estão inscritos em cada torneio
        total_players = c.execute(''' SELECT COUNT(player_id) FROM users_tournaments WHERE tournament_id = ?''', [tournament_id]).fetchone()[0] * 2

        # Quantas o numero maximo de vagas deste torneio
        maximum_slots = int(c.execute(''' SELECT maximum_slots FROM tournaments WHERE id = ?''',[tournament_id]).fetchone()[0])
                
        username = session["username"]
        user = c.execute(''' SELECT user FROM tournaments WHERE id = ?''',[tournament_id]).fetchone()[0]
        
        if username != user:
            error = "Only the user that created the tournament can update them!"

        if error == "":
            return render_template("update.html",tournament = tournament, description = description, gender = gender, level = level, club = club, tournament_date = tournament_date, subscription_date = subscription_date, total_players = total_players, maximum_slots = maximum_slots)
    
        else:
            return render_template("tournaments.html", error=error, tournaments=tournaments)

    else:
        today = str(date.today())

        if today > tournament_date:
            error = "The tournament must be after today!"

        if not club or not level or not gender or not tournament_date or not subscription_date or not description or not maximum_slots:
            
            error = "Information missing!"

        if subscription_date > tournament_date or subscription_date == tournament_date:
            error = "Register date must be before the tournament date!"
          
        if error == "":
            # Update tournament information
            c.execute('''UPDATE tournaments 
                        SET club = ?, level = ?, gender = ?, tournament_date = ?, subscription_date = ?, maximum_slots = ?, description = ? WHERE id = ?''', 
                        (club, level, gender, tournament_date, subscription_date, maximum_slots, description, tournament_id)) 

            connie.commit()  
            
            return redirect("/tournaments")

        else:
            return render_template("update.html", tournament=tournament, level = level, gender = gender, maximum_slots = maximum_slots, error = error)

@app.route("/tournament/<tournament_id>/deregister", methods=["POST"])
def deregister(tournament_id):
    
    # Select tournament
    tournament = c.execute(''' SELECT * FROM tournaments WHERE id = ?''',[tournament_id]).fetchone()
    # Quantos users já estão inscritos em cada torneio
    total_players = c.execute(''' SELECT COUNT(player_id) FROM users_tournaments WHERE tournament_id = ?''', [tournament_id]).fetchone()[0] * 2
   
    # Quantas o numero maximo de vagas deste torneio
    maximum_slots = int(c.execute(''' SELECT maximum_slots FROM tournaments WHERE id = ?''',[tournament_id]).fetchone()[0])

    subscribed_players = c.execute(''' SELECT * FROM users_tournaments WHERE tournament_id = ?''', [tournament_id]).fetchall()
    
    # Players subscribed in this tournament
    players = c.execute(''' SELECT player_username FROM users_tournaments WHERE tournament_id = ?''', [tournament_id]).fetchall()
    
    # Partners subscribed in this tournament
    partners = c.execute(''' SELECT partner_username FROM users_tournaments WHERE tournament_id = ?''', [tournament_id]).fetchall()
    
    # List of all the players subscribed in this tournament
    all_players = list(map(lambda x:x[0], players)) + list(map(lambda x:x[0], partners))
    
    # check if user is subscribed in this tournament
    is_enrolled = session["username"] in all_players 
    
    subscription_date = c.execute(''' SELECT subscription_date FROM tournaments WHERE id = ?''',[tournament_id]).fetchone()[0]
    error = ""
    today = str(date.today())

    if today > subscription_date:
        error = "The deadline to deregister in this tournament its over!"

    if error == "":
        player_username = session["username"]

        # Deresgister players with teammates
        deregister_players(player_username)

        # Number of players registered in tournament
        n_players = c.execute(''' SELECT n_players FROM tournaments WHERE id = ?''',[tournament_id]).fetchone()[0]

        # Decrease number of players registered in tournament
        n_players = n_players - 2 
        c.execute('''UPDATE tournaments SET n_players = ? WHERE id = ?''',(n_players, tournament_id))
        connie.commit()

        return redirect("/tournament/" + tournament_id)

    else:
        return render_template("tournament.html", tournament = tournament, subscribed_players = subscribed_players,
        total_players = total_players, maximum_slots = maximum_slots, is_enrolled = is_enrolled, error = error)



@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug = True)


