import logging
from pathlib import Path

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()
SQL = Path() / 'data' / f'{__name__}.db'

if not SQL.exists():
    SQL.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f'sqlite:///{SQL}', echo=False)
_session_maker = sessionmaker(bind=engine)


def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_session():
    Base.metadata.create_all(bind=engine)
    return _session_maker()
