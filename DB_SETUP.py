import sqlite3

con = sqlite3.connect("RiskCache.db")
cur = con.cursor()

# Create Table
cur.execute("""CREATE TABLE MapCache (
                    mapHash char(32), 
                    playerHash char(32), 
                    score DOUBLE,
                    UNIQUE(mapHash, playerHash)
                );""")

con.commit()

con.close()
