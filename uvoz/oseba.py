# uvozimo ustrezne podatke za povezavo
import auth as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
    CREATE TABLE oseba (
        id SERIAL UNIQUE PRIMARY KEY NOT NULL,
        emso TEXT NOT NULL UNIQUE,
        ime TEXT NOT NULL,
        priimek TEXT NOT NULL,
        ulica TEXT NOT NULL,
        hisna_stevilka INTEGER NOT NULL,
        email TEXT NOT NULL unique,
        telefon TEXT NOT NULL,
        posta_id INTEGER REFERENCES posta(postna_stevilka) NOT NULL,
        uporabnisko_ime TEXT,
        geslo TEXT
    );
    """) 
    conn.commit()

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE oseba CASCADE;
    """)
    conn.commit()

def uvozi_podatke():
    with open("podatki/oseba.csv", encoding="utf-8", errors='ignore') as f:
        rd = csv.reader(f)
        next(rd)
        i= 1 # izpusti naslovno vrstico
        for r in rd:
            cur.execute("""
                INSERT INTO oseba
                (id, emso,ime,priimek,ulica, hisna_stevilka, email,telefon, posta_id, uporabnisko_ime, geslo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [i] + r)
            i = i + 1
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

#pobrisi_tabelo()
#ustvari_tabelo()
#uvozi_podatke()