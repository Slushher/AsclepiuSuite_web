from sqlalchemy.sql import text
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Placeholder auth details now
# Also the code is messy but it gets the job done
login = 'login'
password = 'password'
debugging = 'debugging' 
ip = '127.0.0.1:5000'

is_debug = True

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{login}:{password}@{ip}/{debugging}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def query_login(user_id):
    query = text("SELECT id_apteki FROM `API_VALIDATION` WHERE id_apteki LIKE :user_id;")
    try:
        # Execute the query
        result = db.session.execute(query, {'user_id': f'%{user_id}%'})

        # Fetch the data
        data = result.fetchall()
        if(is_debug):
            print(data[0][0])
        if user_id == str(data[0][0]):
            return True
        else:
            return False

    except Exception as e:
        # Handle exceptions
        print(f"Error executing query: {e}")
        return "An error occurred"

def query_password(user_passsword):
    query = text("SELECT password FROM `API_VALIDATION` WHERE password LIKE :user_passsword;")
    try:
        # Execute the query
        result = db.session.execute(query, {'user_passsword': f'%{user_passsword}%'})

        # Fetch the data
        data = result.fetchall()
        if(is_debug):
            print(data[0][0])
        if user_passsword == str(data[0][0]):
            return True
        else:
            return False

    except Exception as e:
        # Handle exceptions
        print(f"Error executing query: {e}")
        return "An error occurred"
    
def query_meds():
    query = text("SELECT * FROM `leki`;")
    try:
        result = db.session.execute(query)
        data = result.fetchall()
        return data
    except Exception as e:
        print(f"Error executing query: {e}")
        return "An error occurred"

def query_precriptions(pesel = None, access_key = None):
    if pesel is None and access_key is None:
        return False
    else:
        query = text("SELECT * FROM `e-recepty`.`recepty_zbiorcze` WHERE kod_dostepu LIKE :access_key AND pesel = :pesel;")
        result = db.session.execute(query, {'access_key': f'%{access_key}%', 'pesel': pesel})
        rows = result.fetchall()
        id_recepty_zbiorczej = []
        data_array = []
        for row in rows:
            print(row)
            id_recepty_zbiorczej.append(row[0])
        for id_recepty in id_recepty_zbiorczej:
            query = text("SELECT `nazwa_leku`, `ilosc_opakowan`, `ilosc_tabletek`, `dawka`, `odpłatnosć` FROM `e-recepty`.`recepty_jed` WHERE id_recepty_zbiorczej LIKE :id_recepty_zbiorczej;")
            result = db.session.execute(query, {'id_recepty_zbiorczej': f'%{id_recepty}%'})
            data = result.fetchall()
            data_array.append(data)
        return data_array

def add_meds(nazwa_leku = None, ilosc_tabletek = None, dawka = None, ilosc_opakowan = None, waznosc = None, cena = None, substancja_czynna = None):
    query = text("SELECT MAX(`id_leku`) FROM `leki`;")
    result = db.session.execute(query)
    rows = result.fetchall()
    id_lek = int(rows[0][0])
    if(is_debug):
        print("Latest ID = " + str(id_lek))
    new_id = id_lek + 1
    if(is_debug):
        print("New ID = " + str(new_id))
    query = text("INSERT INTO `leki` (`id_leku`, `nazwa_leku`, `Ilosc tabletek`, `dawka`, `Ilosc opakowan`, `Waznosc`, `cena`, `Substancja_czynna`) "
                 "VALUES (:id, :nazwa_leku, :ilosc_tabletek, :dawka, :ilosc_opakowan, :waznosc, :cena, :substancja_czynna);")
    parameters = {
        'id': new_id,
        'nazwa_leku': nazwa_leku,
        'ilosc_tabletek': ilosc_tabletek,
        'dawka': dawka,
        'ilosc_opakowan': ilosc_opakowan,
        'waznosc': waznosc,
        'cena': cena,
        'substancja_czynna': substancja_czynna
    }

def sell_meds(nazwa_leku = None, dawka = None, ilosc_opakowan = None):
    try:
        query = text("SELECT * FROM `leki` WHERE `nazwa_leku` LIKE :nazwa_leku AND 'dawka' LIKE :dawka;")
        result = db.session.execute(query, {'nazwa_leku': nazwa_leku, 'dawka': f'%{dawka}%'})
        current_stock = int(rows[0][3])
        print("ID STOCK " + str(current_stock))
        query = text("SELECT `id_paragonu` FROM `historia_sprzedaz`.`historia_sprzedazy_leku`")
        result = db.session.execute(query)
        rows = result.fetchall()
        id_paragonu_last = int(rows[0][0])
        print("ID PARAGONU " + str(id_paragonu_last))


        query = text("INSERT INTO `historia_sprzedaz`.`historia_sprzedazy_leku` (`id_sprzedazy_leku`, `nazwa_leku`, `ilosc_opakowan`, `dawka_leku`, `data_sprzedazy`, `id_paragonu`) VALUES (NULL, :nazwa_leku, :ilosc_opakowan, :dawka_leku, CURDATE(), :id_paragonu);")
        result = db.session.execute(query, {'nazwa_leku': nazwa_leku, 'dawka_leku' : dawka, 'ilosc_opakowan' : ilosc_opakowan, 'id_paragonu' : str(id_paragonu_last+1)})
        

        if current_stock < int(ilosc_opakowan):
            raise Exception("Niewystarczająca ilość leków na stanie")

        new_stock = current_stock - ilosc_opakowan
        query = text("UPDATE `leki` SET `Ilosc_opakowan` = :new_stock WHERE `nazwa_leku` LIKE :nazwa_leku AND `dawka_leku` LIKE :dawka;")
        db.session.execute(query, {'new_stock': new_stock, 'nazwa_leku':nazwa_leku})
        db.session.commit()

        print(f"Sprzedano {ilosc_opakowan} tabletek leku o ID {nazwa_leku}.")

    except Exception as e:
        print("Błąd podczas sprzedaży leku:", str(e))

def sell_history():
    query = text("SELECT * FROM `historia_sprzedazy_leku`;")
    try:
        result = db.session.execute(query)
        data = result.fetchall()
        return data
    except Exception as e:
        print(f"Error executing query: {e}")
        return "An error occurred"

           