import logging
from pathlib import Path

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQL = Path() / 'data' / 'server.db'

Base = declarative_base()

logger = logging.getLogger(__name__)

if not SQL.exists():
    SQL.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f'sqlite:///{SQL}', echo=False)
_session_maker = sessionmaker(bind=engine)


def get_session():
    Base.metadata.create_all(engine)
    return _session_maker()
