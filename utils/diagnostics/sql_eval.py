from sqlalchemy import create_engine, text
engine = create_engine("postgresql://postgres:local_dev_password@localhost:5432/pipeline_db")
with engine.begin() as conn:
    print("ALL RUNS FOR SMPL-VIRAL-REAL:")
    res = conn.execute(text("SELECT run_id, metadata FROM frontend_runs WHERE sample_id='SMPL-VIRAL-REAL'")).fetchall()
    for row in res:
        print(f"Run ID: {row[0]}, Meta keys: {row[1].keys()}")
        print(f"Dag Step: {row[1].get('dag_step')}")
