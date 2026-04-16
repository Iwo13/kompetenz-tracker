"""
Datenbankverbindung via SQLAlchemy zu MSSQL (SQL Server Express)
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Verbindungsstring: Windows-Authentifizierung, kein Passwort nötig
CONN_STR = (
    "mssql+pyodbc:///?odbc_connect="
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=KompetenzTracker;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

engine = create_engine(CONN_STR, echo=False)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    """Dependency: gibt eine DB-Session zurück und schliesst sie danach."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
