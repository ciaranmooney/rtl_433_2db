#! /usr/bin/env python3 
# -*- coding: utf-8 -*-

# A script that runs rtl_433 and logs the json results to an sqlite database.
# 
# Based on the script by jcarduino available at:
# https://github/jcarduino/rtl_433_2db
# 
# Modifications Copyright 2017 Ciarán Mooney

# Notes 
# * The "model" field in the JSON output is the device name

import subprocess
from datetime import datetime
import threading
import queue as Queue
import sqlite3 as sq
import json
import os
import sys
import time

class asyncFileReader(threading.Thread):
    ''' Helper class to implement asynchronous reading of a file
        in a separate thread. Pushes read lines on a queue to
        be consumed in another thread.
    '''

    def __init__(self, fd, queue, log_file=None):
        assert isinstance(queue, Queue.Queue)
        assert callable(fd.readline)
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = queue
        self._log = log_file

    def run(self):
        ''' The body of the tread: read lines and put them on the queue.
        '''
        for line in iter(self._fd.readline, ''):
            if self._log != None:
                with open(self._log, 'w') as log:
                    log.write(line)
                    log.close()

            self._queue.put(line)

    def eof(self):
        ''' Check whether there is no more content to expect.
        '''
        return not self.is_alive() and self._queue.empty()

class initDatabase(object):
    ''' Initialise database with the filelocation, db_file. If no database is
        present, then try and create it.

        Database Schema
        ---
        xxx
    '''

    def __init__(self, sq, db_path):
        '''
        '''
        self.db_path = db_path
        self.sq = sq
        self.connect()
        #except sq.OperationalError:
        #    print("No directory for database")
        
        table_exists = self.cur.execute('''SELECT name FROM sqlite_master 
                                    WHERE type='table' 
                                    AND name='sensor_data';''')
        table_exists = self.cur.fetchone()
        self.close()

        if table_exists == None:
            self.create_tables()
        
        self.max_id = self.get_max_id()

    def create_tables(self):
        ''' Creates a database with the tables described above.
        '''
        self.connect()
        self.cur.execute('''CREATE TABLE sensor_data  
                         (id integer, date text, sensorID int, 
                          temperature_C float, io text)''')
        self.db.commit()
        self.cur.execute('CREATE TABLE current_id (max_id int)')
        self.db.commit()
        self.cur.execute('INSERT INTO current_id values (?)', (0,))
        self.db.commit()
        self.close()

    def connect(self):
        ''' Re-wraps the sqlite3 database connect and cursor functions.
        '''
        self.db = self.sq.connect(self.db_path)
        self.cur = self.db.cursor()
    
    def close(self):
        ''' Re-wraps the sqlite3 database closure function.
        '''
        self.db.close()
    
    def write(self, json_data):
        ''' Takes json_data and writes it to the sqlite database.
            Increments the max_id.
        '''
        timestamp = str(datetime.now())
        self.connect()
        self.cur.execute('''INSERT INTO sensor_data VALUES
                             (?,?,?,?,?)''', 
                             (self.max_id, timestamp, json_data['id'],
                              json_data['temperature_C'], json_data['io'],))
        self.db.commit()
        self.cur.execute("DELETE from current_id WHERE max_id = ?", 
                          (self.max_id,))
        self.db.commit()
        # XXX Remove increment from write. Move to get_max_id.
        self.cur.execute("INSERT INTO current_id values (?)", 
                          (self.max_id + 1,))
        self.db.commit()
        self.close()

        # XXX Remove increment from write. Move to get_max_id.
        self.max_id = self.get_max_id() + 1

    def get_max_id(self):
        ''' Returns the (only) value in the current_id table.
        '''
        self.connect()
        self.cur.execute("SELECT * from current_id;")
        max_id =  self.cur.fetchone()[0]
        self.close()
        return max_id

    def next_max_id(self):
        ''' Returns the next max ID
        '''

        pass

def createPID(PIDFILE):
    ''' Creates a temporary PID file to track if processing is running.
    '''
    pid = str(os.getpid())
    pidfile = PIDFILE 

    if os.path.isfile(pidfile):
        raise alreadyRunning    
    f = open(pidfile, 'w')
    f.write(pid)
    f.close()


def deletePID(PIDFILE):
    '''
    '''
    os.unlink(PIDFILE)

def startSubProcess(rtl_path, database, debug=False, PIDFILE='/tmp/rtl_433_2sqlite.pid'):
    ''' Example of how to consume standard output and standard error of
        a subprocess asynchronously without risk on deadlocking.
    '''

    createPID(PIDFILE)

    if debug == False:
        command = [rtl_path, "-R", "39","-F", "json"]
        print("\nStarting RTL433\n")

    if debug == True:
        # possibly better doing this with a test suite.
        # cant just run the shell script because it doesn't output json
        command = ['/home/ciaran/Code/rtl_433_tests/rtl_433_test.sh']
        print("\nStarting RTL433 - Debug Mode\n")
    
    # Launch the command as subprocess.
    process = subprocess.Popen(command, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)

    # Launch the asynchronous readers of the process' stdout and stderr.
    stdout_queue = Queue.Queue()
    stdout_reader = asyncFileReader(process.stdout, stdout_queue)
    stdout_reader.start()

    stderr_queue = Queue.Queue()
    stderr_reader = asyncFileReader(process.stderr, stderr_queue)
    stderr_reader.start()
   
    # do queue loop, entering data to database
    # Check the queues if we received some output until there is nothing more 
    # to get.
   
    # print(stderr_queue.empty())
    # print(stderr_queue.get())
    # print(stderr_queue.get())
    # print(stderr_queue.get())
    # print(stderr_reader.eof())
    # print(stderr_queue.empty())
    
    while not stdout_reader.eof() or not stderr_reader.eof(): 
        # Show what we received from standard output.
        print('a')
        while not stdout_queue.empty():     # Whilst we have data.
            print('b')
            while not stderr_queue.empty(): # Whilst we have no errors
                print('Starting loop')
                line = stdout_queue.get()
                try:
                    data = json.loads(line.decode("utf-8"))
                    database.write(data) 
                except json.decoder.JSONDecodeError:
                    # Garbled data from RTL_433
                    print('Garbeled data')

            # Sleep a bit before asking the readers again.
            print('Starting sleeping')
            time.sleep(15)
            print('Finished sleeping')
    
    print('Finished looping')
    # Let's be tidy and join the threads we've started.
    try:
        print('Trying to close DB')
        database.close()
    except:
        print('Failed to close DB')

    print('Tying threads')
    stdout_reader.join()
    stderr_reader.join()

    print('Closing subprocessses')
    # Close subprocess' file descriptors.
    process.stdout.close()
    process.stderr.close()

    deletePID(PIDFILE)
