# uvozimo ustrezne podatke za povezavo
import uvoz.auth as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
    CREATE TABLE nepremicnina (
        id SERIAL UNIQUE PRIMARY KEY ,
        velikost INTEGER NOT NULL,
        vrednost INTEGER NOT NULL,
        naslov TEXT NOT NULL,
        leto_izgradnje INTEGER NOT NULL,
        datum_nakupa DATE NOT NULL,
        regija TEXT NOT NULL 
    );
    """) 
    conn.commit()

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE nepremicnina;
    """)
    conn.commit()

def uvozi_podatke():
    with open("podatki/nepremicnine.csv", encoding="utf-16", errors='ignore') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            cur.execute("""
                INSERT INTO nepremicnina
                (id,velikost,vrednost,naslov,leto_izgradnje,datum_nakupa,regija)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, r)
            print("Uvožena nepremicnina %s z ID-jem %s" % (r[3], r[0]))
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

# pobrisi_tabelo()
# ustvari_tabelo()
uvozi_podatke()