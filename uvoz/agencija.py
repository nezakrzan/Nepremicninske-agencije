# uvozimo ustrezne podatke za povezavo
import auth as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
        CREATE TABLE agencija (
            id SERIAL UNIQUE PRIMARY KEY NOT NULL,
            ime_agencije TEXT NOT NULL,
            mesto TEXT NOT NULL,
            postna_st INTEGER REFERENCES posta(postna_stevilka) NOT NULL
            );
    """)
    conn.commit()

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE agencija CASCADE; 
    """)
    conn.commit()

def uvozi_podatke():
    with open("podatki/agencija.csv", encoding="utf-8", errors='ignore') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            cur.execute("""
                INSERT INTO agencija
                (id,ime_agencije,mesto, postna_st)
                VALUES (%s, %s, %s, %s)
                """, r)
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

#pobrisi_tabelo()
#ustvari_tabelo()
#uvozi_podatke()

