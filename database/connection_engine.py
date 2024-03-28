from sqlalchemy import create_engine, MetaData, Table, select
import pandas as pd


class Database:
    def __init__(self):
        self.db_user = 'root'
        self.db_password = 'slavka2024'
        self.db_host = 'localhost'
        self.db_name = 'profsp'
        self.db_url = f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}/{self.db_name}?charset=utf8mb4"
        self.engine = create_engine(self.db_url)

