import os
import pandas as pd
import pyodbc
import sqlalchemy
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.schema import CreateTable
from dotenv import load_dotenv
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MDBProcessor:
    def __init__(self, mdb_file_path):
        """Initialize the MDB processor with file path and PostgreSQL credentials."""
        load_dotenv()  # Load environment variables
        self.mdb_file_path = mdb_file_path
        
        # PostgreSQL connection details
        self.db_host = os.getenv('db_host')
        self.db_user = os.getenv('db_user')
        self.db_password = os.getenv('db_password')
        self.db_name = os.getenv('db_name', 'postgres')
        
        # Create SQLAlchemy engine
        self.engine = self._create_db_engine()
        self.metadata = MetaData()

    def _create_db_engine(self):
        """Create SQLAlchemy engine for PostgreSQL connection."""
        connection_string = (
            f"postgresql://{self.db_user}:{self.db_password}@"
            f"{self.db_host}/{self.db_name}"
        )
        return create_engine(connection_string)

    def get_mdb_schema(self):
        """Extract schema information from MDB file."""
        logger.info("Extracting schema information from MDB...")
        connection = self.connect_to_mdb()
        cursor = connection.cursor()
        
        schema_info = {}
        
        for table_info in cursor.tables(tableType='TABLE'):
            table_name = table_info.table_name.lower()
            schema_info[table_name] = {
                'columns': [],
                'primary_keys': [],
                'foreign_keys': [],
                'indexes': []
            }
            
            # Get column information
            for column in cursor.columns(table=table_name):
                col_name = column.column_name.lower()
                col_type = column.type_name
                nullable = column.nullable
                schema_info[table_name]['columns'].append({
                    'name': col_name,
                    'type': col_type,
                    'nullable': nullable
                })
            
            # Get primary key information
            try:
                for pk in cursor.primaryKeys(table=table_name):
                    schema_info[table_name]['primary_keys'].append(pk.column_name.lower())
            except:
                logger.warning(f"Could not get primary key info for table {table_name}")
            
            # Get foreign key information
            try:
                for fk in cursor.foreignKeys(table=table_name):
                    schema_info[table_name]['foreign_keys'].append({
                        'column': fk.fkcolumn_name.lower(),
                        'ref_table': fk.pktable_name.lower(),
                        'ref_column': fk.pkcolumn_name.lower()
                    })
            except:
                logger.warning(f"Could not get foreign key info for table {table_name}")
            
            # Get index information
            try:
                for idx in cursor.statistics(table=table_name):
                    if idx.index_name:
                        schema_info[table_name]['indexes'].append({
                            'name': idx.index_name.lower(),
                            'column': idx.column_name.lower(),
                            'unique': not bool(idx.non_unique)
                        })
            except:
                logger.warning(f"Could not get index info for table {table_name}")
        
        connection.close()
        return schema_info

    def map_mdb_to_sql_type(self, mdb_type):
        """Map MDB data types to PostgreSQL data types."""
        type_mapping = {
            'TEXT': String,
            'MEMO': String,
            'BYTE': Integer,
            'INTEGER': Integer,
            'LONG': Integer,
            'SINGLE': sqlalchemy.Float,
            'DOUBLE': sqlalchemy.Float,
            'CURRENCY': sqlalchemy.Numeric,
            'DATETIME': DateTime,
            'BINARY': sqlalchemy.LargeBinary,
            'BOOLEAN': sqlalchemy.Boolean,
        }
        return type_mapping.get(mdb_type.upper(), String)

    def create_tables_with_metadata(self, schema_info):
        """Create tables with proper schema in PostgreSQL."""
        logger.info("Creating tables with metadata...")
        
        for table_name, info in schema_info.items():
            # Create columns
            columns = []
            for col in info['columns']:
                sql_type = self.map_mdb_to_sql_type(col['type'])
                columns.append(Column(
                    col['name'],
                    sql_type,
                    nullable=col['nullable']
                ))
            
            # Create table
            table = Table(table_name, self.metadata, *columns)
            
            # Add primary keys
            if info['primary_keys']:
                pk_constraint = sqlalchemy.PrimaryKeyConstraint(*info['primary_keys'])
                table.append_constraint(pk_constraint)
            
            # Create indexes
            for idx in info['indexes']:
                Index(
                    f"{table_name}_{idx['column']}_idx",
                    table.c[idx['column']],
                    unique=idx['unique']
                )
        
        # Create all tables
        self.metadata.create_all(self.engine)
        
        # Add foreign keys in a second pass
        with self.engine.connect() as connection:
            for table_name, info in schema_info.items():
                for fk in info['foreign_keys']:
                    query = text(f"""
                        ALTER TABLE {table_name}
                        ADD CONSTRAINT fk_{table_name}_{fk['column']}
                        FOREIGN KEY ({fk['column']})
                        REFERENCES {fk['ref_table']}({fk['ref_column']});
                    """)
                    try:
                        connection.execute(query)
                        connection.commit()
                    except Exception as e:
                        logger.warning(f"Could not create foreign key in {table_name}: {str(e)}")

    def connect_to_mdb(self):
        """Create a connection to the MDB file."""
        conn_str = (
            r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
            rf"DBQ={self.mdb_file_path};"
        )
        return pyodbc.connect(conn_str)

    def read_tables(self):
        """Read all tables from the MDB file."""
        logger.info("Reading tables from MDB file...")
        connection = self.connect_to_mdb()
        tables = {}
        
        for table_info in connection.cursor().tables(tableType='TABLE'):
            table_name = table_info.table_name
            logger.info(f"Reading table: {table_name}")
            query = f"SELECT * FROM [{table_name}]"
            tables[table_name] = pd.read_sql(query, connection)
        
        connection.close()
        return tables

    def clean_data(self, tables):
        """Clean the data according to requirements."""
        logger.info("Cleaning data...")
        cleaned_tables = {}
        
        for table_name, df in tables.items():
            # Remove any trailing/leading whitespace
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].str.strip()
            
            # Convert date columns (assuming standard date column names)
            date_columns = [col for col in df.columns if 'DATE' in col.upper() or 'IDO' in col.upper()]
            for col in date_columns:
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    logger.warning(f"Could not convert {col} to datetime in table {table_name}")
            
            # Replace empty strings with None
            df = df.replace(r'^\s*$', None, regex=True)
            
            # Drop duplicate rows
            df = df.drop_duplicates()
            
            # Convert column names to lowercase for PostgreSQL compatibility
            df.columns = [col.lower() for col in df.columns]
            
            cleaned_tables[table_name.lower()] = df
            
        return cleaned_tables

    def upload_to_postgres(self, cleaned_tables):
        """Upload cleaned data to PostgreSQL database."""
        logger.info("Uploading to PostgreSQL...")
        
        try:
            # Test connection
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                logger.info("Successfully connected to PostgreSQL")
                
                for table_name, df in cleaned_tables.items():
                    logger.info(f"Uploading table: {table_name}")
                    
                    # Upload dataframe to PostgreSQL
                    df.to_sql(
                        name=table_name,
                        con=self.engine,
                        if_exists='replace',  # Replace if table exists
                        index=False,
                        method='multi',  # Faster for larger datasets
                        chunksize=1000  # Process in chunks to manage memory
                    )
                    logger.info(f"Successfully uploaded {table_name}")
                    
        except Exception as e:
            logger.error(f"Error uploading to PostgreSQL: {str(e)}")
            raise

    def process(self):
        """Run the complete pipeline."""
        try:
            # Get schema information
            schema_info = self.get_mdb_schema()
            
            # Create tables with proper schema
            self.create_tables_with_metadata(schema_info)
            
            # Read tables
            tables = self.read_tables()
            
            # Clean data
            cleaned_tables = self.clean_data(tables)
            
            # Upload to PostgreSQL
            self.upload_to_postgres(cleaned_tables)
            
            logger.info("Pipeline completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error in pipeline: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage
    mdb_path = "forras/PUPHA_20240301_v3.mdb"
    processor = MDBProcessor(mdb_path)
    processor.process() 