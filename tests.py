#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Tests for the rtl_433_2db.py
# Ciarán Mooney 2017

import unittest
from rtl_433_2db import initDatabase
import sqlite3 as sq
import os

class TestDatabaseInit(unittest.TestCase):
    ''' Tests that the database is created as expected and it's methods all
        behave as expected.
    '''

    def setUp(self):
        '''
        '''
        self.sq_db = sq
        self.db_path = "/tmp/test_db.sqlite"
        self.db = initDatabase(self.sq_db, self.db_path)

    def tearDown(self):
        '''
        '''
        os.remove(self.db_path)

    def test_init_tables(self):
        ''' Tests that when a database is initialised that it contains the
            expected tables.
        '''
        self.db.cur.execute('''SELECT name FROM sqlite_master 
                                            WHERE type='table' AND 
                                            name='sensor_data';''')
        table = self.db.cur.fetchone()
        self.assertEqual(table, ('sensor_data',))
        
    def test_init_table_headers(self):
        ''' Tests that when a database is initialised that the tables have the
            expected headers.
        '''
        pass
    
    def test_init_table_max_id(self):
        ''' Tests that when a database is initialised that the max ID is 
            correct. 
        '''
        pass

    def test_create_tables(self):
        '''
        '''
        pass

    def test_close(self):
        '''
        '''
        pass

    def test_write(self):
        '''
        '''
        pass

    def test_max_id(self):
        '''
        '''
        pass

if __name__ == "__main__":
    unittest.main()

