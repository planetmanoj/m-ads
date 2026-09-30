from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

# For Production, swap to PostgreSQL:
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/ad_db"
SQLALCHEMY_DATABASE_URL = "sqlite:///./ad_server.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} # check_same_thread only needed for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    advertiser = Column(String)
    type = Column(String)
    url = Column(String)
    active = Column(Boolean, default=True)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)

# Create tables
Base.metadata.create_all(bind=engine)
