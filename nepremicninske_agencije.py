#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottleext import *

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import os
import hashlib

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

# Zakomentiraj, če ne želiš sporočil o napakah
debug = True

skrivnost = "rODX3ulHw3ZYRdbIVcp1IfJTDn8iQTH6TFaNBgrSkjIulr"

def nastaviSporocilo(sporocilo = None):
    # global napakaSporocilo
    staro = request.get_cookie("sporocilo", secret=skrivnost)
#    if sporocilo is None:
#        bottle.Response.delete_cookie(key='sporocilo', path='/', secret=skrivnost)
#    else:
#        bottle.Response.set_cookie(key='sporocilo', value=sporocilo, path="/", secret=skrivnost)
    return staro 

# Funkcije za izgradnjo strani

# Statične datoteke damo v mapo 'static' in do njih pridemo na naslovu '/static/...'
# Uporabno za slike in CSS, poskusi http://localhost:8080/static/slika.jpg
@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')

def preveriUporabnika(): 
    uporabnisko_ime = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    if uporabnisko_ime:
       # cur = baza.cursor()    
        uporabnik = None
        try: 
            cur.execute("SELECT * FROM oseba WHERE uporabnisko_ime = %s", [uporabnisko_ime])
            uporabnik = cur.fetchone()
        except:
            uporabnik = None
        if uporabnik: 
            return uporabnik
    redirect(url('/prijava'))

########################## ZAČETNA STRAN ##########################
#začetna stran
@get('/')
def hello():
    return template('prijava.html')

def preveriAgenta(): 
    uporabnisko_ime = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    if uporabnisko_ime:
        cur = conn.cursor() 
        cur.execute("SELECT * FROM oseba WHERE uporabnisko_ime = %s", [uporabnisko_ime])
        uporabnik = cur.fetchone()
        try: 
            cur.execute('SELECT * FROM agent WHERE id_agent = %s', (uporabnik[1], ))
            agent = cur.fetchone()
        except:
            agent = None
        if agent: 
            return True
        else:
            return False
    redirect(url('/nepremicnina'))


########################## PRIJAVA, REGISTRACIJA, ODJAVA, SPREMEBA GESLA ##########################
def preveriUporabnika(): 
    uporabnisko_ime = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    if uporabnisko_ime:
       # cur = baza.cursor()    
        uporabnik = None
        try: 
            cur.execute("SELECT * FROM oseba WHERE uporabnisko_ime = %s", [uporabnisko_ime])
            uporabnik = cur.fetchone()
        except:
            uporabnik = None
        if uporabnik: 
            return uporabnik
    redirect(url('/prijava'))

def hashGesla(s):
    m = hashlib.sha256()
    m.update(s.encode("utf-8"))
    return m.hexdigest()

@get('/registracija')
def registracija_get():
    napaka = nastaviSporocilo()
    return template('registracija.html', napaka=napaka)

@post('/registracija')
def registracija_post():
    emso = request.forms.id
    ime = request.forms.ime
    priimek = request.forms.priimek
    ulica = request.forms.ulica
    hisna_stevilka = request.forms.hisna_stevilka
    email = request.forms.email
    telefon = request.forms.telefon
    posta_id = request.forms.posta_id
    uporabnisko_ime = request.forms.uporabnisko_ime
    geslo = request.forms.geslo
    geslo2 = request.forms.geslo2
    agencija = request.forms.agencija
    tip = request.forms.tip
    placa = request.forms.placa
    kupuje_nepremicnino = request.forms.kupuje_nepremicnino
    njegov_agent = request.forms.njegov_agent
    if uporabnisko_ime is None or geslo is None or geslo2 is None:
        nastaviSporocilo('Registracija ni možna') 
        redirect(url('/registracija'))
        return
    oseba = cur 
    uporabnik = None
    try: 
        uporabnik = cur.execute("SELECT * FROM oseba WHERE uporabnisko_ime = ?", [uporabnisko_ime])
    except:
        uporabnik = None
    if uporabnik is not None:
        nastaviSporocilo('Registracija ni možna') 
        redirect(url('/registracija'))
        return
    if len(geslo) < 4:
        nastaviSporocilo('Geslo mora imeti vsaj 4 znake.') 
        redirect(url('/registracija'))
        return
    if geslo != geslo2:
        nastaviSporocilo('Gesli se ne ujemata.') 
        redirect(url('/registracija_get'))
        return
     
    zgostitev = hashGesla(geslo)
    cur.execute("""INSERT INTO oseba
                (emso,ime,priimek,ulica, hisna_stevilka, email,telefon, posta_id, uporabnisko_ime, geslo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (emso,ime,priimek,ulica, hisna_stevilka, email,telefon, posta_id, uporabnisko_ime, zgostitev))
    response.set_cookie('uporabnisko_ime', uporabnisko_ime, secret=skrivnost)
    if tip == 'agent':
        cur.execute("""INSERT INTO agent
                (id_agent, agencija, plača)
                VALUES (%s, %s, %s)""", (emso, agencija, placa))
    if tip == 'komitent':
        cur.execute("""INSERT INTO komitent
                (id_komitent,kupuje_nepremicnino, njegov_agent)
                VALUES (%s, %s, %s)""", (emso, kupuje_nepremicnino, njegov_agent))
    response.set_cookie('uporabnisko_ime', uporabnisko_ime, secret=skrivnost)      
    redirect(url('prijava_get'))

@get('/prijava')
def prijava_get():
    return template('prijava.html')

@post('/prijava')
def prijava_post():
    uporabnisko_ime = request.forms.uporabnisko_ime
    geslo = request.forms.geslo
    if uporabnisko_ime is None or geslo is None:
        nastaviSporocilo('Uporabniško ima in geslo morata biti neprazna') 
        redirect(url('/prijava'))
        return
    oseba = cur   
    hashBaza = None
    try: 
        hashBaza = cur.execute("SELECT geslo FROM oseba WHERE uporabnisko_ime = %s", (uporabnisko_ime, ))
        hashBaza = cur.fetchone()
        hashBaza = hashBaza[0]
    except:
        hashBaza = None
    if hashBaza is None:
        nastaviSporocilo('Uporabniško geslo ali ime nista ustrezni') 
        redirect(url('/prijava'))
        return
    if hashGesla(geslo) == hashBaza or geslo == hashBaza:
        response.set_cookie('uporabnisko_ime', uporabnisko_ime, secret=skrivnost)
        
        redirect(url('/podatki_prijavljenega'))
        return
    else:
        nastaviSporocilo('Uporabniško geslo ali ime nista ustrezni') 
        redirect(url('/prijava'))
        return

@get('/index')
def index():
    if preveriAgenta():
        return template('agent_stran.html')
    else:
        return template('komitent_stran.html')
  
@get('/odjava')
def odjava():
    response.delete_cookie('uporabnisko_ime')
    redirect(url('/prijava'))

@get('/spremeni_geslo')
def spremeni_geslo():
    napaka = nastaviSporocilo()
    uporabnik = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    return template('spremeni_geslo.html')

@post('/spremeni_geslo')
def spremeni_geslo_post():
    uporabnik = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    geslo = request.forms.geslo
    geslo2 = request.forms.geslo2
    if geslo != geslo2:
        nastaviSporocilo('Gesli se ne ujemata') 
        redirect(url('/spremeni_geslo'))
        return
    if len(geslo) < 4:
        nastaviSporocilo('Geslo mora vsebovati vsaj štiri znake') 
        redirect(url('/spremeni_geslo'))
        return 
    cur = conn.cursor()
    if uporabnik:    
        uporabnik1 = None
        uporabnik2 = None
        try: 
            cur = conn.cursor()
            cur.execute("SELECT * FROM oseba WHERE uporabnisko_ime = %s", (uporabnik, ))
            uporabnik1 = cur.fetchone()
        except:
            uporabnik1 = None
        try: 
            cur = conn.cursor()
            cur.execute("SELECT * FROM oseba WHERE uporabnisko_ime = %s", (uporabnik, ))
            uporabnik2 = cur.fetchone()            
        except:
            uporabnik2 = None    
        if uporabnik1: 
            zgostitev1 = hashGesla(geslo)
            cur.execute("UPDATE oseba SET  geslo = %s WHERE uporabnisko_ime = %s", (zgostitev1 ,uporabnik))
            conn.commit()
            return redirect(url('/prijava'))
        if uporabnik2:
            zgostitev2 = hashGesla(geslo)
            cur.execute("UPDATE oseba SET  geslo = %s WHERE uporabnisko_ime = %s", (zgostitev2 ,uporabnik))
            conn.commit()
            return redirect(url('/prijava'))
    nastaviSporocilo('Obvezna registracija') 
    redirect(url('/registracija'))

@get('/oseba')
def oseba():
    cur.execute("""
    SELECT emso, ime, priimek, ulica, hisna_stevilka, email, telefon, posta.postna_stevilka , posta.posta, uporabnisko_ime, geslo FROM oseba
    INNER JOIN posta ON posta.postna_stevilka = oseba.posta_id
    ORDER BY oseba.priimek """)
    return template('oseba.html', oseba=cur)
    
########################## DODAJANJE KOMITENTA ##########################
@get('/dodaj_komitenta')
def dodaj_komitenta():
    return template('dodaj_komitenta.html', id='', ime='', priimek='', ulica='', hisna_stevilka='', email='', telefon='', posta_id='', uporabnisko_ime='', geslo='', napaka=None)

@post('/dodaj_komitenta')
def dodaj_komitenta_post():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    id = request.forms.id
    ime = request.forms.ime
    priimek = request.forms.priimek
    ulica = request.forms.ulica
    hisna_stevilka = request.forms.hisna_stevilka
    email = request.forms.email
    telefon = request.forms.telefon
    posta_id = request.forms.posta_id
    uporabnisko_ime = request.forms.uporabnisko_ime
    geslo = request.forms.geslo
    geslo1 = hashGesla(geslo)
    tip  = request.forms.tip
    kupuje_nepremicnino = request.forms.kupuje_nepremicnino
    njegov_agent = request.forms.njegov_agent

    cur.execute("""INSERT INTO oseba
                (emso,ime,priimek,ulica, hisna_stevilka, email,telefon, posta_id, uporabnisko_ime, geslo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (id,ime,priimek,ulica, hisna_stevilka, email,telefon, posta_id, uporabnisko_ime, geslo1))
    response.set_cookie('uporabnisko_ime', uporabnisko_ime, secret=skrivnost)
    if tip == 'komitent':
        cur.execute("""INSERT INTO komitent
                (id_komitent,kupuje_nepremicnino, njegov_agent)
                VALUES (%s, %s, %s)""", (id, kupuje_nepremicnino, njegov_agent))
    response.set_cookie('uporabnisko_ime', uporabnisko_ime, secret=skrivnost)      
    redirect(url('/komitent'))

########################## UREJANJE KOMITENTA ##########################
@get('/uredi_ulico')
def uredi_ulico():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    return template('uredi_ulico.html', ulica='')

@post('/uredi_ulico')
def uredi_ulico_post():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    uporabnisko_ime = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    ulica = request.forms.ulica

    cur.execute("UPDATE oseba SET ulica=%s WHERE uporabnisko_ime=%s",
                    (ulica, uporabnisko_ime))
    conn.commit()
    redirect(url('podatki_prijavljenega'))

@get('/uredi_priimek')
def uredi_priimek():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    return template('uredi_priimek.html', priimek='')

@post('/uredi_priimek')
def uredi_priimek_post():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    uporabnisko_ime = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    priimek = request.forms.priimek

    cur.execute("UPDATE oseba SET priimek=%s WHERE uporabnisko_ime=%s",
                    (priimek, uporabnisko_ime))
    conn.commit()
    redirect(url('podatki_prijavljenega'))

@get('/uredi_hisno_stevilko')
def uredi_hisno_stevilko():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    return template('uredi_hisno_stevilko.html', priimek='')

@post('/uredi_hisno_stevilko')
def uredi_hisno_stevilko_post():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    uporabnisko_ime = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    hisna_stevilka = request.forms.hisna_stevilka

    cur.execute("UPDATE oseba SET hisna_stevilka=%s WHERE uporabnisko_ime=%s",
                    (hisna_stevilka, uporabnisko_ime))
    conn.commit()
    redirect(url('podatki_prijavljenega'))

@get('/uredi_email')
def uredi_email():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    return template('uredi_email.html', priimek='')

@post('/uredi_email')
def uredi_email_post():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    uporabnisko_ime = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    email = request.forms.email

    cur.execute("UPDATE oseba SET email=%s WHERE uporabnisko_ime=%s",
                    (email, uporabnisko_ime))
    conn.commit()
    redirect(url('podatki_prijavljenega'))

@get('/uredi_telefon')
def uredi_telefon():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    return template('uredi_telefon.html', priimek='')

@post('/uredi_telefon')
def uredi_email_post():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    uporabnisko_ime = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    telefon = request.forms.telefon

    cur.execute("UPDATE oseba SET telefon=%s WHERE uporabnisko_ime=%s",
                    (telefon, uporabnisko_ime))
    conn.commit()
    redirect(url('podatki_prijavljenega'))

@get('/uredi_posto')
def uredi_posto():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    return template('uredi_posto.html', priimek='')

@post('/uredi_posto')
def uredi_posto_post():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    uporabnisko_ime = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    posta_id = request.forms.posta_id

    cur.execute("UPDATE oseba SET posta_id=%s WHERE uporabnisko_ime=%s",
                    (posta_id, uporabnisko_ime))
    conn.commit()
    redirect(url('podatki_prijavljenega'))

########################## IZBRIS KOMITENTA ##########################
@post('/izbrisi_komitenta/<id>')
def izbrisi_komitenta(id):
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    uporabnisko_ime = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    cur.execute("DELETE FROM komitent WHERE id_komitent=%s",
                    [id])
    redirect(url('/komitent'))

########################## PODATKI PRIJAVLJENEGA ##########################
@get('/podatki_prijavljenega')
def podatki_prijavljenega():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    uporabnisko_ime = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    cur.execute("""SELECT uporabnisko_ime,ime,priimek,ulica,hisna_stevilka,email,telefon,posta_id
                FROM oseba WHERE uporabnisko_ime=%s""",[uporabnisko_ime])
    if preveriAgenta():
        return template('podatki_prijavljenega.html', oseba=cur)
    else:
        return template('podatki_prijavljenega_komitent.html', oseba=cur)

########################## DODAJANJE AGENTA ##########################
@get('/dodaj_agenta')
def dodaj_agenta():
    return template('dodaj_agenta.html', id='', ime='', priimek='', ulica='', hisna_stevilka='', email='', telefon='', posta_id='', uporabnisko_ime='', geslo='', napaka=None)

@post('/dodaj_agenta')
def dodaj_agenta_post():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    id = request.forms.id
    ime = request.forms.ime
    priimek = request.forms.priimek
    ulica = request.forms.ulica
    hisna_stevilka = request.forms.hisna_stevilka
    email = request.forms.email
    telefon = request.forms.telefon
    posta_id = request.forms.posta_id
    uporabnisko_ime = request.forms.uporabnisko_ime
    geslo = request.forms.geslo
    geslo1 = hashGesla(geslo)
    tip  = request.forms.tip
    agencija = request.forms.agencija
    tip = request.forms.tip
    placa = request.forms.placa

    cur.execute("""INSERT INTO oseba
                (emso,ime,priimek,ulica, hisna_stevilka, email,telefon, posta_id, uporabnisko_ime, geslo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (id,ime,priimek,ulica, hisna_stevilka, email,telefon, posta_id, uporabnisko_ime, geslo1))
    response.set_cookie('uporabnisko_ime', uporabnisko_ime, secret=skrivnost)
    if tip == 'agent':
        cur.execute("""INSERT INTO agent
                (id_agent, agencija, plača)
                VALUES (%s, %s, %s)""", (id, agencija, placa))
    response.set_cookie('uporabnisko_ime', uporabnisko_ime, secret=skrivnost)      
    redirect(url('/agent'))

########################## DODAJANJE NEPREMIČNINE ##########################
@get('/dodaj_nepremicnino')
def dodaj_nepremicnino():
    return template('dodaj_nepremicnino.html', napaka=None)

@post('/dodaj_nepremicnino')
def dodaj_nepremicnino_post():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    id = request.forms.id
    velikost = request.forms.velikost
    cena = request.forms.cena
    ulica = request.forms.ulica
    hisna_stevilka = request.forms.hisna_stevilka
    postna_stevilka = request.forms.postna_stevilka
    leto_izgradnje = request.forms.leto_izgradnje
    kupuje_agencija = request.forms.kupuje_agencija
    tip = request.forms.tip
    bazen = request.forms.bazen
    igrisce= request.forms.igrisce
    velikost_vrta=request.forms.velikost_vrta
    nadstropje = request.forms.nadstropje
    balkon = request.forms.balkon
    parkirisce = request.forms.parkirisce

    cur.execute("INSERT INTO nepremicnina (id,velikost,cena,ulica,hisna_stevilka, postna_stevilka, leto_izgradnje, kupuje_agencija) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (id,velikost,cena,ulica,hisna_stevilka, postna_stevilka, leto_izgradnje, kupuje_agencija))
    if tip == 'hisa':
        cur.execute(""" INSERT INTO hisa
                (id_hisa,bazen,igrisce,velikost_vrta)
                VALUES (%s, %s, %s, %s)""", (id,bazen,igrisce,velikost_vrta))
    if tip == 'stanovanje':
        cur.execute(""" INSERT INTO stanovanje
                (id_stanovanje,nadstropje, balkon, parkirisce)
                VALUES (%s, %s, %s, %s)""", (id,nadstropje, balkon, parkirisce))
    redirect(url('/nepremicnina'))

########################## IZBRIS NEPREMICNIN ##########################
@post('/izbrisi_nepremicnino/<id>')
def izbrisi_nepremicnino(id):
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    uporabnisko_ime = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    cur.execute("DELETE FROM hisa WHERE id_hisa =%s", [id])
    cur.execute("DELETE FROM stanovanje WHERE id_stanovanje=%s", [id])
    cur.execute("DELETE FROM komitent WHERE kupuje_nepremicnino=%s", [id])
    cur.execute("DELETE FROM nepremicnina WHERE id =%s" ,[id])
    conn.commit()
    redirect(url('/nepremicnina'))



########################## UREJANJE NEPREMICNINE ##########################
@get('/uredi_nepremicnino/<id>')
def uredi_nepremicnino(id):
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    return template('uredi_nepremicnino.html', id=id)

@post('/uredi_nepremicnino/<id>')
def uredi_nepremicnino_post(id):
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    cena = request.forms.cena
    cur.execute("UPDATE nepremicnina SET cena=%s WHERE id=%s " ,
                    (cena, id))
    conn.commit()
    redirect(url('nepremicnina'))

########################## TABELE ##########################
@get('/komitent')
def komitent():
    cur.execute("""
    SELECT id_komitent, oseba.ime, oseba.priimek, kupuje_nepremicnino, njegov_agent FROM komitent
    LEFT JOIN oseba ON komitent.id_komitent = oseba.emso
     """)
    return template('komitent.html', komitent=cur)

@get('/agencija')
def agencija():
    cur.execute("""
    SELECT id,ime_agencije,mesto, postna_st FROM agencija
     """)
    if preveriAgenta():
        return template('agencija.html', agencija=cur)
    else:
        return template('agencije_komitenti.html', agencija=cur)


@get('/agenti_agencije_get/<x:int>/')
def agenti_agencije_get(x):
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    cur.execute("""SELECT id_agent,oseba.ime,oseba.priimek, oseba.telefon, oseba.email
                FROM agent 
                LEFT JOIN oseba ON oseba.emso = agent.id_agent
                WHERE agencija = %s""", [x])
    return template('agenti_agencije.html', x=x, agent=cur)

@get('/agent')
def agent():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    cur.execute("""
    SELECT id_agent, oseba.ime, oseba.priimek, plača, agencija, agencija.ime_agencije FROM agent
    LEFT JOIN oseba ON agent.id_agent = oseba.emso
    LEFT JOIN agencija ON agent.agencija = agencija.id
     """)
    return template('agent.html', agent=cur)

@get('/posta')
def posta():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    cur.execute("""
        SELECT * FROM posta
    """)
    return template('posta.html', posta=cur)

@get('/nepremicnina')
def nepremicnina():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    cur.execute("""
        SELECT nepremicnina.id, velikost, cena, ulica, hisna_stevilka, postna_stevilka, leto_izgradnje, kupuje_agencija FROM nepremicnina
        INNER JOIN agencija ON agencija.id = nepremicnina.kupuje_agencija
    """)
    if preveriAgenta():
        return template('nepremicnina.html', nepremicnina=cur)
    else:
        return template('nepremicnina_komitent.html', nepremicnina=cur)

@get('/hisa')
def hisa():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    cur.execute("""
        SELECT id_hisa,bazen,igrisce,velikost_vrta, cena, ulica, hisna_stevilka, posta.postna_stevilka, posta.posta, leto_izgradnje, kupuje_agencija, agencija.ime_agencije FROM hisa
        INNER JOIN nepremicnina ON nepremicnina.id = id_hisa
        INNER JOIN posta ON posta.postna_stevilka = nepremicnina.postna_stevilka
        INNER JOIN agencija ON agencija.id = nepremicnina.kupuje_agencija
    """)
    return template('hisa.html', hisa=cur)

@get('/stanovanja')
def stanovanja():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    cur.execute("""
        SELECT id_stanovanje,nadstropje, balkon, parkirisce, cena, ulica, hisna_stevilka, posta.postna_stevilka, posta.posta, leto_izgradnje, kupuje_agencija, agencija.ime_agencije FROM stanovanje
        INNER JOIN nepremicnina ON nepremicnina.id = id_stanovanje
        INNER JOIN posta ON posta.postna_stevilka = nepremicnina.postna_stevilka
        INNER JOIN agencija ON agencija.id = nepremicnina.kupuje_agencija
    """)
    return template('stanovanje.html', stanovanja=cur)

######################################################################
# Glavni program
# tu bi se priklopili na bazo

# Poženemo strežnik na portu 8080, glej http://localhost:8080/
# Iz bottle dokumentacije o parametru reloader=True: Every time you edit a module file, 
# the reloader restarts the server process and loads the newest version of your code. 
conn = psycopg2.connect(database='sem2022_ninav', host='baza.fmf.uni-lj.si', user='javnost', password='javnogeslo')
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogocimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
run(host='localhost', port=8080, reloader=True)

######################################################################