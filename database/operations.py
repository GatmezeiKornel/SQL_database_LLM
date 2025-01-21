from sqlalchemy.orm import Session
import pandas as pd
from sqlalchemy import text
from typing import Optional

class DatabaseOperations:
    def __init__(self, session: Session):
        self.session = session
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a raw SQL query and return results as DataFrame"""
        try:
            result = self.session.execute(text(query))
            columns = result.keys()
            data = result.fetchall()
            return pd.DataFrame(data, columns=columns)
        except Exception as e:
            self.session.rollback()
            raise e

    def execute_parameterized_query(self, query: str, params: dict) -> pd.DataFrame:
        """Execute a parameterized query with proper SQL injection protection"""
        try:
            result = self.session.execute(text(query), params)
            columns = result.keys()
            data = result.fetchall()
            return pd.DataFrame(data, columns=columns)
        except Exception as e:
            self.session.rollback()
            raise e

    def commit(self):
        """Commit the current transaction"""
        self.session.commit()

    def rollback(self):
        """Rollback the current transaction"""
        self.session.rollback() 