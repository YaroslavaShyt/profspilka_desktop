from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Float

metadata = MetaData()

roles = Table('roles', metadata,
              Column('id', Integer, primary_key=True, autoincrement=True),
              Column('title', String(20))
              )

faculties = Table('faculties', metadata,
                  Column('id', Integer, primary_key=True, autoincrement=True),
                  Column('title', String(20))
                  )

members = Table('members', metadata,
                Column('id', Integer, primary_key=True, autoincrement=True, unique=True, ),
                Column('name', String(20)),
                Column('surname', String(20)),
                Column('role', Integer, ForeignKey('roles.id')),
                Column('faculty', Integer, ForeignKey('faculties.id'))
                )

expenses = Table('expenses', metadata,
                 Column('id', Integer, primary_key=True),
                 Column('id_member', Integer, ForeignKey('members.id')),
                 Column('amount', Float),
                 Column('purpose', String),
                 Column('year', Integer)
                 )
