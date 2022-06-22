# uvozimo ustrezne podatke za povezavo
import auth as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
    CREATE TABLE nepremicnina (
        id SERIAL UNIQUE PRIMARY KEY NOT NULL,
        velikost INTEGER NOT NULL,
        cena INTEGER NOT NULL,
        ulica TEXT NOT NULL,
        hisna_stevilka INTEGER NOT NULL,
        postna_stevilka INTEGER REFERENCES posta(postna_stevilka) NOT NULL,
        leto_izgradnje INTEGER NOT NULL,
        kupuje_agencija INTEGER REFERENCES agencija(id) NOT NULL 
    );
    """) 
    conn.commit()

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE nepremicnina CASCADE;
    """)
    conn.commit()

def uvozi_podatke():
    with open("podatki/nepremicnina.csv", encoding="utf-8", errors='ignore') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            cur.execute("""
                INSERT INTO nepremicnina
                (id,velikost,cena,ulica,hisna_stevilka, postna_stevilka, leto_izgradnje, kupuje_agencija)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, r)
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

#pobrisi_tabelo()
#ustvari_tabelo()
#uvozi_podatke()