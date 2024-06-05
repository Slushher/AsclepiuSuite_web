from flask import Flask, render_template, request, redirect, url_for
from flask import send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash, check_password_hash
from db import *

@app.route('/')
def main():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template("index.html")

@app.route('/przypomnij')
def przypomnij():
    return render_template("przypomnij.html")

@app.route('/process_login', methods=['POST'])
def process_login():
    if request.method == 'POST':
        login_text = request.form.get('login_text')
        password_text = request.form.get('password_text')
        if(is_debug):
            print("login_text : " + login_text)
            print("password_text : " + password_text)

        login_result = query_login(login_text)
        print(login_result)
        password_result = query_password(password_text)
        print(password_result)
        if login_result & password_result:
            return redirect('/apteka')
        else:
            return redirect('/login')
        
@app.route('/historia')
def historia():
    return render_template("historia.html",meds=sell_history())

@app.route('/apteka')
def login_success():
    return render_template("landing.html")

@app.route('/stan')
def stan():
    return render_template("stan.html", meds=query_meds())

@app.route('/recepta', methods=['GET', 'POST'])
def recepta():
    if request.method == 'POST':
        pesel = request.form.get('pesel')
        kod_dostepu = request.form.get('kod_dostepu')
        if pesel != None and kod_dostepu != None:
            return render_template("erecepty.html", meds=query_precriptions(pesel, kod_dostepu))
    else:
        return render_template("erecepty.html")

@app.route('/magazyn', methods=['GET', 'POST'])
def magazyn():
    if request.method == 'POST':
        nazwa_leku = request.form.get('nazwa_leku')
        ilosc_tabletek = request.form.get('ilosc_tabletek')
        dawka = request.form.get('dawka')
        ilosc_opakowan = request.form.get('ilosc_opakowan')
        waznosc = request.form.get('waznosc')
        cena = request.form.get('cena')
        substancja_czynna = request.form.get('substancja_czynna')
        if nazwa_leku != None and ilosc_tabletek != None and dawka != None and ilosc_opakowan != None and waznosc != None and cena != None and substancja_czynna != None:
            add_meds(nazwa_leku, ilosc_tabletek, dawka, ilosc_opakowan, waznosc, cena, substancja_czynna)
            return render_template("magazyn.html")
    return render_template("magazyn.html")

@app.route('/zamowienia', methods=['GET', 'POST'])
def zamowienia():
    if request.method == 'POST':
        nazwa_leku = request.form.get('nazwa_leku')
        ilosc_tabletek = request.form.get('ilosc_tabletek')
        dawka = request.form.get('dawka')
        ilosc_opakowan = request.form.get('ilosc_opakowan')
        waznosc = request.form.get('waznosc')
        cena = request.form.get('cena')
        substancja_czynna = request.form.get('substancja_czynna')
        if nazwa_leku != None and ilosc_tabletek != None and dawka != None and ilosc_opakowan != None and waznosc != None and cena != None and substancja_czynna != None:
            add_meds(nazwa_leku, ilosc_tabletek, dawka, ilosc_opakowan, waznosc, cena, substancja_czynna)
            return render_template("zamowienia.html")
    return render_template("zamowienia.html")

@app.route('/sprzedaz', methods=['GET', 'POST'])
def sprzedaz():
    if request.method == 'POST':
        nazwa_leku = request.form.get('nazwa_leku')
        dawka = request.form.get('dawka')
        print("Dawka : " + dawka)
        ilosc_opakowan = request.form.get('ilosc_opakowan')
        print(f"Sprzedano {nazwa_leku} {dawka}  {ilosc_opakowan}.")
        if nazwa_leku != None  and dawka != None and ilosc_opakowan != None:
            sell_meds(nazwa_leku, dawka, ilosc_opakowan)
            return render_template("sprzedaz.html")
    return render_template("sprzedaz.html")

if __name__ == '__main__':
    app.run(debug=True)
