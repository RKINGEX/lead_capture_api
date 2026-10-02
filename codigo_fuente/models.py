from sqlalchemy import Column, Integer, String
from codigo_fuente.database import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String, unique=True)
    request = Column(String)
    notes = Column(String)
    temperature = Column(String, nullable=True)


