from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL construction
connection_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.environ["db_user"],
    password=os.environ["db_password"],
    host=os.environ["db_host"],
    database="pupha",
    port=5432  # default PostgreSQL port
)

# Create engine
engine = create_engine(
    connection_url,
    pool_pre_ping=True,  # enables connection health checks
    pool_size=5,  # connection pool size
    max_overflow=10  # max number of connections that can be created beyond pool_size
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()