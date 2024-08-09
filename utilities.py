#!/usr/bin/python3
import chromadb
import logging
import os
import sys

def get_chromadb_client():
    return chromadb.HttpClient(host='localhost', port=8000)


def check_env_var_exists(env_var):
    '''
    Check that the given environment variable exists
    and exit with an error message if it doesn't
    '''
    value=os.getenv(env_var)

    if not value:
        logging.error(f"'{env_var}' not declared")
        sys.exit(1)

    if len(value.rstrip()) != len(value):
        logging.error(f"'{env_var}' has trailing whitespace")
        sys.exit(1)
