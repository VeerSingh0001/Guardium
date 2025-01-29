from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine('sqlite:///viruses.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Allow(Base):
    __tablename__ = "allowed"
    sr_no = Column(Integer, primary_key=True)
    id = Column(String)
    name = Column(String)
    path = Column(String, unique=True)
    severity = Column(String)

class Quarantine(Base):
    __tablename__ = "quarantined"
    sr_no = Column(Integer, primary_key=True)
    id = Column(String)
    name = Column(String)
    quarantined_name = Column(String, unique=True)
    path = Column(String, unique=True)
    quarantined_path = Column(String, unique=True)
    severity = Column(String)

class Data:
    def __init__(self):
        Base.metadata.create_all(engine)

    def add_allowed(self, vid, vname, vpath, vseverity):
        with Session() as session:
            new_virus = Allow(id=vid, name=vname, path=vpath, severity=vseverity)
            session.add(new_virus)
            session.commit()

    def add_quarantine(self, vid, vname, vqname, vpath, vqpath, vseverity):
        with Session() as session:
            new_virus = Quarantine(id=vid, name=vname, quarantined_name=vqname, path=vpath, quarantined_path=vqpath, severity=vseverity)
            session.add(new_virus)
            session.commit()

    def check_path_exists(self, vpath):
        with Session() as session:
            return session.query(Allow).filter_by(path=vpath).first() or session.query(Quarantine).filter_by(path=vpath).first()

    def get_all_allowed(self):
        with Session() as session:
            return session.query(Allow).all()

    def get_all_quarantined(self):
        with Session() as session:
            return session.query(Quarantine).all()

    def get_quarantined_path(self, file_path):
        with Session() as session:
            return session.query(Quarantine.quarantined_path).filter_by(path=file_path).first()

    def remove_quarantined(self, q_file_path):
        with Session() as session:
            session.query(Quarantine).filter_by(quarantined_path=q_file_path).delete()
            session.commit()

    def remove_allowed(self, file_path):
        with Session() as session:
            session.query(Allow).filter_by(path=file_path).delete()
            session.commit()
