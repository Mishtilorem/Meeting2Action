import os
from db import conn

sql_path = os.path.join(os.path.dirname(__file__), "schema.sql")
with conn() as c:
    c.execute(open(sql_path, encoding="utf-8").read())
print("tables ready")
