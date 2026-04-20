import os
import subprocess
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

# Connect to the AWS Database via the active localhost SSM Tunnel
db_host = os.environ.get("DB_HOST", "localhost")
db_password = os.environ.get("DB_PASSWORD", "postgres")
engine = create_engine(f"postgresql+psycopg2://postgres:{db_password}@{db_host}:5432/pipeline_db", isolation_level="AUTOCOMMIT")

with engine.connect() as conn:
    print("Creating security roles etl_worker and frontend_api...")
    try:
        conn.execute(text("CREATE ROLE etl_worker WITH LOGIN PASSWORD 'strong_etl_password';"))
    except ProgrammingError as e:
        print("etl_worker exists, skipping...")
    
    try:
        conn.execute(text("CREATE ROLE frontend_api WITH LOGIN PASSWORD 'strong_frontend_password';"))
    except ProgrammingError as e:
        print("frontend_api exists, skipping...")

    print("Granting basic connection rights...")
    conn.execute(text("GRANT CONNECT ON DATABASE pipeline_db TO etl_worker, frontend_api;"))
    conn.execute(text("GRANT USAGE ON SCHEMA public TO etl_worker, frontend_api;"))

print("Running Alembic to formulate the architectural tables...")
subprocess.run(["venv/bin/alembic", "upgrade", "head"], check=True)

with engine.connect() as conn:
    print("Building relational Table Triggers...")
    with open("db-init/03_triggers.sql", "r") as f:
        # Pass the entire script natively to perfectly preserve $$ PL/pgSQL structures
        conn.execute(text(f.read()))
    print("Triggers correctly activated on the active instance!")
