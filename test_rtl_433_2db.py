#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Tests for the rtl_433_2db.py
# Ciarán Mooney 2017

import unittest
import unittest.mock as mock
import rtl_433_2db

from datetime import datetime
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
        self.db = rtl_433_2db.initDatabase(sq, self.db_path)
        self.db.connect()

    def tearDown(self):
        ''' Deletes the database to make sure it doesn't confuse us.
        '''
        self.db.close()
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
        
    @mock.patch.object(sq, 'connect')
    def test_close(self, mock_connect):
        '''
        '''
        sqlite_connect_mock = mock.Mock()
        mock_connect.return_value = sqlite_connect_mock
        # Connect has to be called so that mock object is used. 
        # Connect called previously in setUp, but this uses the original
        # sqlite objecct.
        self.db.connect()
        self.db.close()
        self.assertTrue(sqlite_connect_mock.close.called, True)
   
    @mock.patch.object(sq,'connect')
    def test_connect(self, mock_method):
        '''
        '''
        self.db.close()
        self.db.connect()
        mock_method.assert_called_with(self.db_path)

    def test_write(self):
        '''
        '''
        with mock.patch('rtl_433_2db.datetime') as mock_timestamp:
            n = datetime.now()
            mock_timestamp.now.return_value = n
            mock_timestamp.side_effect = lambda * args, **kw: datetime.now(*args, **kw)
            assert rtl_433_2db.datetime.now() == n

            test_json = {"time" : "@0.000000s", "model" : "WG-PB12V1", 
                         "id" : 8, "temperature_C" : 20.900, 
                         "io" : "111111110011001001100001011010001111111101001100"}
            
            # Test that id starts at zero. 
            self.db.cur.execute('''SELECT * FROM current_id;''')
            table = self.db.cur.fetchone()
            self.assertEqual(0, table[0])
            
            # Check that data is written.
            self.db.write(test_json)
            self.db.connect()
            self.db.cur.execute("SELECT * FROM sensor_data")
            data = self.db.cur.fetchall()[0]
            self.assertEqual(data[0], 0)
            self.assertEqual(data[1], str(n))
            self.assertEqual(data[2], 8)
            self.assertEqual(data[3], 20.9)
            self.assertEqual(data[4], 
                         '111111110011001001100001011010001111111101001100')

            # Check that the id incremented.    
            self.db.cur.execute('''SELECT * FROM current_id;''')
            table = self.db.cur.fetchone()
            self.assertEqual(1, table[0])

    def test_get_max_id(self):
        '''
        '''
        test_json = {"time" : "@0.000000s", "model" : "WG-PB12V1", 
                     "id" : 8, "temperature_C" : 20.900, 
                     "io" : "111111110011001001100001011010001111111101001100"}
            
        # Test that id starts at zero. 
        self.db.cur.execute('''SELECT * FROM current_id;''')
        table = self.db.cur.fetchone()
        self.assertEqual(0, table[0])
            
        self.db.write(test_json)

        # Check that the id incremented.    
        self.db.connect()
        self.db.cur.execute('''SELECT * FROM current_id;''')
        table = self.db.cur.fetchone()
        self.assertEqual(1, table[0])

    def testNewMaxID(self):
        ''' 
        '''
        
        self.assertTrue(False)


class TestAsyncFileReader(unittest.TestCase):
    ''' Tests the asyncFileReaderClass.
    '''

    @mock.patch('output_file')
    @mock.patch('queue_class')
    @mock.patch('process_out')
    def testInit(self, mock_processOut, mock_queueClass, mock_outputFile):
        '''
        '''
        test_queue = rtl_433_2db.asyncFileReader(mock_processOut, mock_queueClass,
                                                    mock_outputFile)
        #push data into filereader - somehow.
        test_queue.run()
        #check that queu now contains data
        #check that output file now contains data

class TestRTL433recordings(unittest.TestCase):
    ''' Tests that the correct data is stored when the recordings from
        RTL 433 tests are used for the WG-PB12v1
    '''

    def setUp(self):
        '''
        '''

        pass

class TestRTL433Errors(unittest.TestCase):
    '''
    '''

    def init(self):
        '''
        '''

        pass

if __name__ == "__main__":
    unittest.main()

