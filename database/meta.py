from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

all = (
    'METADATA',
    'Base'
)

convention = {
    'ix': 'ix%(column_0label)s',
    'uq': 'uq%(tablename)s%(column_0name)s',
    'ck': 'ck%(tablename)s%(constraintname)s',
    'fk': 'fk%(tablename)s%(column_0name)s%(referred_tablename)s',
    'pk': 'pk%(table_name)s',
}

METADATA = MetaData(
    schema='public',
    naming_convention=convention
)

''' Контейнер для декларирования ОРМ моделей '''

Base = declarative_base(metadata=METADATA)

'''Базовый класс для создания ОРМ моделей '''



