#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Tests for the rtl_433_2sqlite.py
# Ciarán Mooney 2017

import unittest
from unittest.mock import Mock
from unittest.mock import patch
from unittest.mock import mock_open

from datetime import datetime
import sqlite3 as sq
import os
import psutil

import queue as Queue
from json.decoder import JSONDecodeError

import rtl_433_2sqlite

class CallableExhausted(Exception):
    '''
    '''
    pass

class ErrorAfter(object):
    ''' Callable that will raise `CallableExhausted`
        exception after `limit` calls
    '''

    def __init__(self, limit):
        self.limit = limit
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self.calls > self.limit:
            #raise CallableExhausted
            return True
        return False 

class TestDatabaseInit(unittest.TestCase):
    ''' Tests that the database is created as expected and it's methods all
        behave as expected.
    '''

    def setUp(self):
        '''
        '''
        db_path = '/tmp/test_db.sqlite'
        try:
            os.remove(db_path)
        except FileNotFoundError:
            # Not a problem.
            pass

        self.db_path = "/tmp/test_db.sqlite"
        self.db = rtl_433_2sqlite.initDatabase(sq, self.db_path)
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
        
    @patch.object(sq, 'connect')
    def test_close(self, mock_connect):
        '''
        '''
        sqlite_connect_mock = Mock()
        mock_connect.return_value = sqlite_connect_mock
        # Connect has to be called so that mock object is used. 
        # Connect called previously in setUp, but this uses the original
        # sqlite objecct.
        self.db.connect()
        self.db.close()
        self.assertTrue(sqlite_connect_mock.close.called, True)
   
    @patch.object(sq,'connect')
    def test_connect(self, mock_method):
        '''
        '''
        self.db.close()
        self.db.connect()
        mock_method.assert_called_with(self.db_path)

    def test_write(self):
        '''
        '''
        with patch('rtl_433_2sqlite.datetime') as mock_timestamp:
            n = datetime.now()
            mock_timestamp.now.return_value = n
            mock_timestamp.side_effect = lambda * args, **kw: datetime.now(*args, **kw)
            assert rtl_433_2sqlite.datetime.now() == n

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

class testCreatePID(unittest.TestCase):
    '''
    '''
    
    def testCreatePID(self):
        ''' Checks that a file with the correct PID is created.
        '''
        self.assertTrue(False)

class testDeletePID(unittest.TestCase):
    '''
    '''
    
    def testDeletePID(self):
        '''
        '''
        self.assertTrue(False)


class TestAsyncFileReader(unittest.TestCase):
    ''' Tests the asyncFileReaderClass.
    '''

    def setUp(self):
        '''
        '''

        self.mock_processOut = Mock()
        self.mock_queueClass = Mock(spec=Queue.Queue())
        self.test_queue = rtl_433_2sqlite.asyncFileReader(self.mock_processOut, 
                                                        self.mock_queueClass)

    def testInit(self):
        ''' Tests that when asyncFileReader is passed data that it is written
            to the log file.
        '''
        
        self.mock_processOut.readline.side_effect=['hello', 'world','','foo']
        self.test_queue.run()
        not_expected = [(('hello',),), (('world',),), (('',),), (('foo',),)]
        self.assertNotEqual(self.test_queue._queue.put.call_args_list, not_expected)
        expected = [(('hello',),), (('world',),)]
        self.assertEqual(self.test_queue._queue.put.call_args_list, expected)

    @patch('builtins.open')
    def testRTLDataLogged(self, m_open):
        ''' Check that when a log file is specified that it actually calls
            file.write() with data.
        '''

        mock_processOut = Mock()
        mock_queueClass = Mock(spec=Queue.Queue())
        test_queue = rtl_433_2sqlite.asyncFileReader(mock_processOut, mock_queueClass,
                                                    log_file='/tmp/test.tmp')
        mock_processOut.readline.side_effect=['hello', 'world','','foo']
        test_queue.run()
        m_open.assert_called_with('/tmp/test.tmp', 'w')
        handle = m_open().__enter__()
        expected = [(('hello',),), (('world',),)]
        self.assertEqual(handle.write.call_args_list, expected)
        
class TestRTL433recordings(unittest.TestCase):
    ''' Tests that the correct data is stored when the recordings from
        RTL 433 tests are used for the WG-PB12v1
    '''

    def setUp(self):
        '''
        '''
        pass

class TestRTL433Errors(unittest.TestCase):
    ''' Test that checks that rtl_433_2sqlite handles errors from rtl_433
        gracefully.
    '''

    def setUp(self):
        '''
        '''
        if 'rtl_433_2sqlite.pid' in os.listdir('/tmp'):
            pid_file = open('/tmp/rtl_433_2sqlite.pid', 'r')
            pid_id = pid_file.readline()
            pid_file.close()
            if pid_id in psutil.pids():
                raise alreadyRunning
            else:
                os.unlink('/tmp/rtl_433_2sqlite.pid')

        if 'rtl_433.pid' in os.listdir('/tmp'):
            pid_file = open('/tmp/rtl_433.pid', 'r')
            pid_id = pid_file.readline()
            pid_file.close()
            if pid_id in psutil.pids():
                raise alreadyRunning
            else:
                os.unlink('/tmp/rtl_433.pid')

    def tearDown(self):
        ''' Removes the rtl_433_2sqlite.pid file after a test has finished.
            Just incase the test didn't
        '''
        try:
            os.unlink('/tmp/rtl_433_2sqlite.pid')
            os.unlink('/tmp/rtl_433.pid')
        except FileNotFoundError:
            pass
            #print('rtl_433_2sqlite.pid already deleted')

    @patch('time.sleep', return_value=None)
    @patch.object(Queue.Queue, 'empty', side_effect=ErrorAfter(3))
    @patch.object(Queue.Queue, 'get')
    @patch.object(rtl_433_2sqlite.asyncFileReader, 'eof', side_effect=ErrorAfter(2))
    def testBlankResponse(self, mock_eof, mock_get, mock_empty, mock_sleep):
        ''' Sends a blank ('') response from rtl_433 to rtl_433_2sqlite.
        '''
        DB_FILE = "/tmp/tempdb.sqlite"
        RTL433 = "/home/ciaran/Code/rtl_433/build/src/rtl_433"
        DEBUG = False
      
        empty_string = ''.encode()
        mock_get.return_value = empty_string
        db = rtl_433_2sqlite.initDatabase(sq, DB_FILE)
        try:
            rtl_433_2sqlite.startSubProcess(RTL433, db, DEBUG)
        except CallableExhausted:
            # To catch the error thown by second loop
            print('Error\'d')
        self.assertTrue(False) # What is this test actualy testing?

    @patch.object(Queue.Queue, 'empty', side_effect=ErrorAfter(4))
    @patch.object(Queue.Queue, 'get')
    def testGoodBadGoodResponse(self, mock_get, mock_empty):
        ''' Sends a "good" RTL_433 response, then a "bad" (blank) response, 
            then good again.

            Test should continue without any faults.
        '''
        DB_FILE = "/tmp/tempdb.sqlite"
        RTL433 = "/home/ciaran/Code/rtl_433/build/src/rtl_433"
        DEBUG = False 
        self.assertTrue(False)
        empty_string = ''.encode()
        good_string = ('{"time" : "@0.000000s",'
                       ' "model" : "WG-PB12V1",'
                       ' "id" : 8,'
                       ' "temperature_C" : 20.900,'
                       ' "io" : "111111110011001001100001011010001111111101001100"}').encode()
        mock_get.side_effect = [good_string, empty_string, good_string]
        db = rtl_433_2sqlite.initDatabase(sq, DB_FILE)
        try:
            rtl_433_2sqlite.startSubProcess(RTL433, db, DEBUG)
        except CallableExhausted:
            # To catch the error thrown by third loop, see ErrorAfter()
            pass

    def testRTL4332sqlitePID(self):
        ''' Test that when RTL_433_2sqlite been run that the PID file is
            created with the corred PID.
        '''
        self.assertTrue(False)

    def testRTL4332sqliteRunning(self):
        ''' Check that a PID file is created for the subprocess with the
            correct PID.
        '''
        self.assertTrue(False)

    def testRTL433subprocesPID(self):
        ''' Test that when the program has been run that the PID 
        '''
        self.assertTrue(False)

class TestRTL433Running(unittest.TestCase):
    '''
    '''
    
    def setUp(self):
        '''
        '''
        pass

    def testRunning(self):
        ''' Creates two processes and checks than error is raised.
        '''
        self.assertTrue(False)

    def testRunningAfterCrash(self):
        ''' Tests that when a process crashes, leaving a PID file in /tmp that
            the script checks the PID, replaces the pid in the PID file and 
            starts running.
        '''
        self.assertTrue(False)

if __name__ == "__main__":
    unittest.main()

