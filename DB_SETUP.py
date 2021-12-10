import sqlite3

con = sqlite3.connect("RiskCache.db")
cur = con.cursor()

# Create Table
cur.execute("""CREATE TABLE MapCache 
                (mapHash char(32), playerHash char(32), score DOUBLE);""")

con.commit()

con.close()
