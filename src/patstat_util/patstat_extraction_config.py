"""
Created on Sun April 11 2021

@author: Antoine Mathieu Collin
@email: antoine.mathieu-collin@kuleuven.be
@article: This code is part of the article: "XXXX"

@description: We define a series of SQL queries in order to retrieve the relevant information from the PATSTAT database, hosted locally in a PostgreSQL database.
"""

# Imports
import pandas as pd
from sqlalchemy import inspect
from sqlalchemy import create_engine

# Imports custom modules
import data_variables as var # names of the PATSTAT data variables
import read_sql_tmpfile as rSQLtemp # snippet to speed up large SQL queries by loading them in a temporary file
import settings


class ConfigPatstat:
    """Configuration of the data-retrival engine"""
    
    PASTAT_location = settings.PASTAT_location
    
    sql_query_PATENT_PRIMARY_INFO = """
            SELECT tls201_appln.appln_id, tls201_appln.DOCDB_FAMILY_ID,tls201_appln.EARLIEST_FILING_DATE, tls201_appln.EARLIEST_FILING_YEAR, tls201_appln.NB_CITING_DOCDB_FAM, cpc_class_symbol
            FROM tls201_appln JOIN tls224_appln_cpc ON tls201_appln.appln_id = tls224_appln_cpc.appln_id
            WHERE cpc_class_symbol like '{}%%'
            AND appln_filing_year between {} and {}
            ORDER BY tls201_appln.appln_id
            """
    
    sql_query_PATENT_MAIN_INFO = """
            SELECT * 
            FROM temporary_table_patent_ids
            LEFT JOIN tls201_appln ON temporary_table_patent_ids.appln_id = tls201_appln.appln_id
            LEFT JOIN TLS202_APPLN_TITLE ON temporary_table_patent_ids.appln_id = TLS202_APPLN_TITLE.appln_id
            LEFT JOIN TLS203_APPLN_ABSTR ON temporary_table_patent_ids.appln_id = TLS203_APPLN_ABSTR.appln_id
            LEFT JOIN TLS209_APPLN_IPC ON temporary_table_patent_ids.appln_id = TLS209_APPLN_IPC.appln_id
            LEFT JOIN TLS229_APPLN_NACE2 ON temporary_table_patent_ids.appln_id = TLS229_APPLN_NACE2.appln_id
            LEFT JOIN TLS211_PAT_PUBLN ON temporary_table_patent_ids.appln_id = TLS211_PAT_PUBLN.appln_id
            """

    sql_query_CPC_INFO = """
            SELECT * 
            FROM temporary_table_patent_ids
            LEFT JOIN TLS224_APPLN_CPC ON temporary_table_patent_ids.appln_id = TLS224_APPLN_CPC.appln_id 
            """
    
    sql_query_PATENTEES_INFO = """
            SELECT * 
            FROM temporary_table_patent_ids
            LEFT JOIN TLS207_PERS_APPLN ON temporary_table_patent_ids.appln_id = TLS207_PERS_APPLN.appln_id
            LEFT JOIN TLS206_PERSON ON TLS207_PERS_APPLN.PERSON_ID = TLS206_PERSON.PERSON_ID
            LEFT JOIN TLS226_PERSON_ORIG ON TLS206_PERSON.PERSON_ID = TLS226_PERSON_ORIG.PERSON_ID
            --LEFT JOIN TLS228_DOCDB_FAM_CITN ON tls201_appln.DOCDB_FAMILY_ID = TLS228_DOCDB_FAM_CITN.DOCDB_FAMILY_ID
            """
    
    sql_query_DOCDB_backwards_citations = """
            SELECT * 
            FROM docdb_family_ids
            LEFT JOIN TLS228_DOCDB_FAM_CITN ON docdb_family_ids.docdb_family_id = TLS228_DOCDB_FAM_CITN.docdb_family_id
            """
    
    sql_query_FORWARD_CITATIONS = """
            SELECT docdb_family_ids.DOCDB_FAMILY_ID, TLS228_DOCDB_FAM_CITN.DOCDB_FAMILY_ID,
            TLS228_DOCDB_FAM_CITN.CITED_DOCDB_FAMILY_ID
            FROM docdb_family_ids JOIN TLS228_DOCDB_FAM_CITN 
            ON docdb_family_ids.DOCDB_FAMILY_ID = TLS228_DOCDB_FAM_CITN.CITED_DOCDB_FAMILY_ID
            """
    
    temp_table_patent_ids = 'temporary_table_patent_ids'
    temp_table_fam_ids = 'docdb_family_ids'