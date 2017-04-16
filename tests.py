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
        self.db_path = "/tmp/test_db.sqlite"
        self.db = initDatabase(sq, self.db_path)

    def tearDown(self):
        ''' Deletes the database to make sure it doesn't confuse us.
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

        self.db.cur.execute('''SELECT name FROM sqlite_master 
                                            WHERE type='table' AND 
                                            name='current_id';''')
        table = self.db.cur.fetchone()
        self.assertEqual(table, ('current_id',))
    
    def test_init_table_headers(self):
        ''' Tests that when a database is initialised that the tables have the
            expected headers.
        '''
        self.db.cur.execute('''PRAGMA table_info('sensor_data');''')
        headers = self.db.cur.fetchall()
        self.assertEqual(headers[0][1], 'id')
        self.assertEqual(headers[1][1], 'date')
        self.assertEqual(headers[2][1], 'sensorID')
        self.assertEqual(headers[3][1], 'temperature_C')
        self.assertEqual(headers[4][1], 'io')
    
    def test_init_table_max_id(self):
        ''' Tests that when a database is initialised that the max ID is 
            correct. 
        '''
        self.db.cur.execute('''SELECT * FROM current_id;''')
        table = self.db.cur.fetchone()
        self.assertEqual(0, table[0])
        
    def test_close(self):
        '''
        '''
        # Candidate for mock.
        self.assertTrue(False)
    
    def test_connect(self):
        '''
        '''
        # Candidate for mock.
        self.assertTrue(False)

    def test_write(self):
        '''
        '''
        test_json = {"time" : "@0.000000s", "model" : "WG-PB12V1", 
                     "id" : 8, "temperature_C" : 20.900, 
                     "io" : "111111110011001001100001011010001111111101001100"}
        
        self.db.cur.execute('''SELECT * FROM current_id;''')
        table = self.db.cur.fetchone()
        self.assertEqual(0, table[0])

        self.db.write(test_json)
        self.db.cur.execute("SELECT * FROM sensor_data")
        data = self.db.cur.fetchall()
        self.assertEqual(data[0][1], 0)
        self.assertEqual(data[1][1], 'date')
        self.assertEqual(data[2][1], 8)
        self.assertEqual(data[3][1], 20.9)
        self.assertEqual(data[4][1], '111111110011001001100001011010001111111101001100')

        self.db.cur.execute('''SELECT * FROM current_id;''')
        table = self.db.cur.fetchone()
        self.assertEqual(1, table[0])
        
        self.assertTrue(False)

    def test_max_id(self):
        '''
        '''
        pass

if __name__ == "__main__":
    unittest.main()

