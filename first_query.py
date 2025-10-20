import sqlite3
import pandas as pd

conn = sqlite3.connect('snapp_dataset.db')

cursor = conn.cursor()

query = """
        SELECT *
        FROM employee
        WHERE LastName LIKE 'Smith%'
        AND TerminationDate IS NULL
        ORDER BY LastName, FirstName;
        """

df = pd.read_sql_query(query, conn)
print(df.to_string(index=False))
conn.close()