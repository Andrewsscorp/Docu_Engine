from sqlalchemy import create_engine, MetaData, text
engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/docuengine")
with engine.connect() as conn:
    res = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'agn_expedientes';"))
    for row in res:
        print(f"{row[0]}: {row[1]}")
