from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

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
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('name', String(20)),
                Column('surname', String(20)),
                Column('role', Integer, ForeignKey('roles.id')),
                Column('faculty', Integer, ForeignKey('faculties.id'))
                )
