#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottleext import *

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

# Zakomentiraj, če ne želiš sporočil o napakah
debug = True

skrivnost = "rODX3ulHw3ZYRdbIVcp1IfJTDn8iQTH6TFaNBgrSkjIulr"

def nastaviSporocilo(sporocilo = None):
    # global napakaSporocilo
    staro = request.get_cookie("sporocilo", secret=skrivnost)
    if sporocilo is None:
        bottle.Response.delete_cookie(key='sporocilo', path='/', secret=skrivnost)
    else:
        bottle.Response.set_cookie(key='sporocilo', value=sporocilo, path="/", secret=skrivnost)
    return staro 

# Funkcije za izgradnjo strani

# Statične datoteke damo v mapo 'static' in do njih pridemo na naslovu '/static/...'
# Uporabno za slike in CSS, poskusi http://localhost:8080/static/slika.jpg
@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')


#začetna stran 
@get('/')
def hello():
    return template('index.html', naslov='nepremicnine')


@get('/oseba')
def oseba():
    cur.execute("""
    SELECT id, ime, priimek, ulica, hisna_stevilka, email, telefon, posta.postna_stevilka , posta.posta FROM oseba
    INNER JOIN posta ON posta.postna_stevilka = oseba.posta_id
    ORDER BY oseba.priimek """)
    return template('oseba.html', oseba=cur)

@get('/dodaj_oseba')
def dodaj_oseba():
    return template('dodaj_oseba.html', id='', ime='', priimek='', ulica='', hisna_stevilka='', email='', telefon='', posta_id='', napaka=None)

@post('/dodaj_oseba')
def dodaj_oseba_post():
    id = request.forms.id
    ime = request.forms.ime
    priimek = request.forms.priimek
    ulica = request.forms.ulica
    hisna_stevilka = request.forms.hisna_stevilka
    email = request.forms.email
    telefon = request.forms.telefon
    posta_id = request.forms.posta_id
    try:
        cur.execute("INSERT INTO oseba (id, ime, priimek, ulica, hisna_stevilka, email, telefon, posta_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (id, ime, priimek, ulica, hisna_stevilka, email, telefon, posta_id))
        conn.commit()
    except Exception as ex:
        conn.rollback()
        return template('dodaj_oseba.html', id=id, ime=ime, priimek=priimek, ulica=ulica, hisna_stevilka=hisna_stevilka, email=email, telefon=telefon, posta_id=posta_id,
                        napaka='Zgodila se je napaka: %s' % ex)
    redirect(url('/oseba'))

@get('/komitent')
def komitent():
    cur.execute("""
    SELECT id_komitent, oseba.ime, oseba.priimek, kupuje_nepremicnino, njegov_agent FROM komitent
    LEFT JOIN oseba ON komitent.id_komitent = oseba.id
     """)
    return template('komitent.html', komitent=cur)

#tabela agenta
@get('/agent')
def agent():
    cur.execute("""
    SELECT id_agent, oseba.ime, oseba.priimek, plača, agencija, agencija.ime FROM agent
    LEFT JOIN oseba ON agent.id_agent = oseba.id
    LEFT JOIN agencija ON agent.agencija = agencija.id
     """)
    return template('agent.html', agent=cur)

@get('/posta')
def posta():
    cur.execute("""
        SELECT * FROM posta
    """)
    return template('posta.html', posta=cur)

@get('/nepremicnina')
def nepremicnina():
    cur.execute("""
        SELECT nepremicnina.id, velikost, cena, ulica, hisna_stevilka, postna_stevilka, leto_izgradnje, kupuje_agencija FROM nepremicnina
        INNER JOIN agencija ON agencija.id = nepremicnina.kupuje_agencija
    """)
    return template('nepremicnina.html', nepremicnina=cur)

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