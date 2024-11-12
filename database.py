from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

# Example: Connect to an SQLite database (use other connection strings for MySQL, PostgresSQL, etc.)
engine = create_engine('sqlite:///viruses.db')

Base = declarative_base()


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
    path = Column(String, unique=True)
    severity = Column(String)


class Data:

    def __init__(self):

        # Create all tables
        Base.metadata.create_all(engine)

        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

    def add_allowed(self,vid, vname, vpath, vseverity):
        new_virus = Allow(
            id=vid,
            name=vname,
            path=vpath,
            severity=vseverity
        )
        self.session.add(new_virus)
        self.session.commit()

    def add_quarantine(self,vid, vname, vpath, vseverity):
        new_virus = Quarantine(
            id=vid,
            name=vname,
            path=vpath,
            severity=vseverity
        )
        self.session.add(new_virus)
        self.session.commit()

    def check_path_exists(self,vpath):
        # Check in the allowed table
        allowed_result = self.session.query(Allow).filter_by(path=vpath).first()

        if allowed_result:
            return True

        # Check in the quarantined table
        quarantined_result = self.session.query(Quarantine).filter_by(path=vpath).first()

        if quarantined_result:
            return True

        return False

    def get_all_allowed(self):
        # Query all records from the `allowed` table
        allowed_viruses = self.session.query(Allow).all()
        return allowed_viruses

    def get_all_quarantined(self):
        # Query all records from the `allowed` table
        allowed_viruses = self.session.query(Quarantine).all()
        return allowed_viruses

