"""
Created on Sun April 11 2021

@author: Antoine Mathieu Collin
@email: antoine.mathieu-collin@kuleuven.be
@article: This code is part of the article: "XXXX"

@description: Creates a simple API to query the PATSTAT database.
"""

import pandas as pd
from sqlalchemy import inspect
from sqlalchemy import create_engine

# custom modules
from patstat_extraction_config import ConfigPatstat 
import data_variables as var # Names of the PATSTAT data variables
import read_sql_tmpfile as rSQLtemp # Snippet to speed up large SQL queries by loading them in a temporary file


class Query:
    """Parameters of the PATSTAT query"""
    
    # Input variables
    technology_classes: list
    start_year: int
    end_year: int
        
    # Output variables
    output_files_prefix: str
        
    def __init__(self, technology_classes, start_year, end_year, output_files_prefix):
        self.technology_classes = technology_classes
        self.start_year = start_year
        self.end_year = end_year
        self.output_files_prefix = output_files_prefix
        
        
class DataRetrievalModel(ConfigPatstat):
    """Engine definition"""
    
    # Model variables 
    
    # Defined with the initialisation
    query: Query
    
    # Defined once the model is fitted
    patent_ids: list
    docdb_ids: list
        
    # Result datasets
    TABLE_MAIN_PATENT_INFOS: pd.DataFrame()
    TABLE_CPC: pd.DataFrame()
    TABLE_PATENTEES_INFO: pd.DataFrame()
    TABLE_DOCDB_BACKWARD_CITATIONS: pd.DataFrame()
    TABLE_DOCDB_FORWARD_CITATIONS: pd.DataFrame()
    
    def __init__(self, query: Query):
        self.query = query
    
    def _connect_engine(self):
        """Creation of the SQL alchemy engine and connection to the database"""
        self.engine = create_engine(ConfigPatstat.PASTAT_location)
        self.connection = self.engine.connect()
        
    def _create_temporary_table(self, df, table_name):
        """Creation of temporary tables in the database"""
        df.to_sql(table_name, self.engine, if_exists="replace")
        
    def _clear_temporary_table(self, table):
        """Clear the temporary table created in the Postgresql database"""
        my_query = 'drop table if exists '+ table
        results = self.connection.execute(my_query)
        
    def _inspect_database_content(self):
        """Returns the name of the tables in the database"""
        return self.engine.table_names()
    
    def _close_connection(self):
        """We close the connection to the database once we are done querying"""
        self._clear_temporary_table(ConfigPatstat.temp_table_patent_ids)
        self._clear_temporary_table(ConfigPatstat.temp_table_fam_ids)
        self.connection.close()
        
    def _get_primary_info(self): 
        """We retrieve the primary information about the patents"""
        
        # We retrieve the data for all technology classes 1 by 1
        # and store the result in a separate dataframe
        list_df = []
        sql = ConfigPatstat.sql_query_PATENT_PRIMARY_INFO
        
        for technology_class in self.query.technology_classes:
            # We insert in the standart query the parameters chosen
            SQL_query = sql.format(technology_class,
                                   self.query.start_year,
                                   self.query.end_year)
            # We retrieve the data via a temporary file for performance
            t = rSQLtemp.read_sql_tmpfile(SQL_query,self.engine)
            list_df.append(t)

        # Update the variable
        self.TABLE_MAIN_PATENT_INFOS = pd.concat(list_df)
        
    def _select_patents_of_interest(self):
        """After the first retrieval of data, one could prune the list of 
        selected patents in case the query would be too large - for instance
        to eliminate Patent with no value (citation count)"""
        
        # We update the list of patent and DOCDB family ids
        self.patent_ids = (self.TABLE_MAIN_PATENT_INFOS
                           [var.PATSTAT_APPLN_ID]
                           .unique().tolist())
        self.docdb_ids = (self.TABLE_MAIN_PATENT_INFOS
                          [var.PATSTAT_DOCDB_FAMILY_ID]
                          .unique().tolist())
    
    def _create_temp_table_with_patent_ids(self):
        """Creating a temporary table in the SQL database contaning the patent ids
        -> Allows to join on this table using SQL afterwards."""
    
        # Definition of the table
        table_name = ConfigPatstat.temp_table_patent_ids
        t = tuple(self.patent_ids)
        df = pd.DataFrame(t)
        df.columns = [var.PATSTAT_APPLN_ID]
        
        # Creation of the temporary table in the SQLAlchemy database
        self._create_temporary_table(df, table_name)
    
    def _get_general_info(self):
        """Retrieving general information about the selected patents"""
        self.TABLE_MAIN_PATENT_INFOS = rSQLtemp.read_sql_tmpfile(
                                            ConfigPatstat.sql_query_PATENT_MAIN_INFO,
                                            self.engine)
        
    def _get_CPC_classes(self):
        "Retrieving CPC technology classes of the selected patents"
        self.TABLE_CPC = rSQLtemp.read_sql_tmpfile(
                                ConfigPatstat.sql_query_CPC_INFO, 
                                self.engine)
       
    def _get_patentees_info(self):
        """Retrieving information about the patentees (individuals) of the selected patents"""
        self.TABLE_PATENTEES_INFO = rSQLtemp.read_sql_tmpfile(
                                    ConfigPatstat.sql_query_PATENTEES_INFO,
                                    self.engine)
        
    def _create_temp_table_with_DOCDB_ids(self):
        """Creating a temporary table in the SQL database containing the
        docdb_family ids to allow joining on this table on later SQL queries"""

        # Definition of the table
        table_name = ConfigPatstat.temp_table_fam_ids
        t = tuple(self.docdb_ids)
        df = pd.DataFrame(t)
        df.columns = [var.PATSTAT_DOCDB_FAMILY_ID]

        # Creation of the temporary table in the SQLAlchemy database
        self._create_temporary_table(df, table_name)
        
    def _retrieve_backward_docdb_citations(self):
        """Retrieving information about backward citations of the selected families"""
        self.TABLE_DOCDB_BACKWARD_CITATIONS = rSQLtemp.read_sql_tmpfile(
            ConfigPatstat.sql_query_DOCDB_backwards_citations,self.engine)
        
    def _retrieve_forward_docdb_citations(self):
        """Retrieving information about forward citations of the selected families"""
        self.TABLE_DOCDB_FORWARD_CITATIONS = rSQLtemp.read_sql_tmpfile(
            ConfigPatstat.sql_query_FORWARD_CITATIONS,self.engine) 
                
    def _export_result_datasets(self):
        """Exporting the result datasets in the data/raw folder"""
        
        pre = '../data/raw/' + self.query.output_files_prefix
        suf = '.csv'
        
        storage_scheme = {'_table_main_patent_infos' : self.TABLE_MAIN_PATENT_INFOS,
                          '_table_cpc' : self.TABLE_CPC,
                          '_table_patentees_info' : self.TABLE_PATENTEES_INFO ,
                          '_table_backward_docdb_citations' : self.TABLE_DOCDB_BACKWARD_CITATIONS,
                          '_table_forward_docdb_citations' : self.TABLE_DOCDB_FORWARD_CITATIONS}
        
        for path, df in storage_scheme.items():
            path = pre + path + suf 
            df.to_csv(path, index=False)