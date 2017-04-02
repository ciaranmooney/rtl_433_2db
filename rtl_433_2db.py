#! /usr/bin/env python 
# -*- coding: utf-8 -*-

# A script that runs rtl_433 and logs the json results to an sqlite database.
# 
# Based on the script by jcarduino available at:
# https://github/jcarduino/rtl_433_2db
# 
# Modifications Copyright 2017 Ciarán Mooney

# import sys

import subprocess
import time
import threading
import Queue
import sqlite3 as sq
import json

# BEGIN CONFIG
DB_FILE = "/var/lib/temperaturedb/tempdb.sqlite"
RTL433 = "/home/ciaran/Code/rtl_433/build/src/rtl_433"
# END CONFIG

class asyncFileReader(threading.Thread):
    ''' Helper class to implement asynchronous reading of a file
        in a separate thread. Pushes read lines on a queue to
        be consumed in another thread.
    '''

    def __init__(self, fd, queue):
        assert isinstance(queue, Queue.Queue)
        assert callable(fd.readline)
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = queue

    def run(self):
        ''' The body of the tread: read lines and put them on the queue.
        '''
        for line in iter(self._fd.readline, ''):
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
        self.db = sq.connect(db_path)
        #except sq.OperationalError:
        #    print("No directory for database")
        
        self.cur = self.db.cursor()
        table_exists = self.cur.execute('''SELECT name FROM sqlite_master 
                                    WHERE type='table' AND name='sensor_data';''')
        table_exists = self.cur.fetchone()
        
        if table_exists == None:
            self.create_tables()
        
        self.max_id = self.get_max_id()

    def create_tables(self):
        ''' Creates a database with the tables described above.
        '''
        self.cur.execute('''CREATE TABLE sensor_data  
                         (id integer, date text, sensorID int, 
                          temperature_C float, io text)''')
        self.db.commit()
        self.cur.execute('CREATE TABLE current_id (max_id int)')
        self.db.commit()
        self.close()

    def close(self):
        ''' Re-wraps the sqlite3 database closure function.
        '''
        self.db.close()

    def write(self, json_data):
        ''' Takes json_data and writes it to the sqlite database.
            Increments the max_id.
        '''
        new_max_id = self.max_id + 1
        self.cur.execute('''INSERT INTO sensor_data VALUES
                          (?,?,?,?,?)", (new_max_id, datetime, data['id'],
                          data['temp'], data['io'])''')
        self.db.commit()
        self.cur.execute("DELETE from current_id WHERE max_id = ?", 
                          (self.max_id,))
        self.db.commit()
        self.cur.execute("INSERT INTO current_id ?", new_max_id)
        self.db.commit()
        self.max_id = self.get_max_id()

    def get_max_id(self):
        ''' Returns the (only) value in the current_id table.
        '''
        self.cur.execute("SELECT * from current_id;")
        return self.cur.fetchone


def startSubProcess(rtl_path, database):
    ''' Example of how to consume standard output and standard error of
        a subprocess asynchronously without risk on deadlocking.
    '''
    command = [rtl_path, "-R", "39","-F", "json"]
    print "\nStarting RTL433\n"
    
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
    # Check the queues if we received some output until there is nothing more to get.
    
    while not stdout_reader.eof() or not stderr_reader.eof():
        # Show what we received from standard output.
        while not stdout_queue.empty():
            # Whilst we have data.
            line = stdout_queue.get()
            print(repr(line))

            while not stderr_queue.empty():
                # Whilst we have no errors
                line = stdout_queue.get()
                data = json.loads(line)
                database.write(data) # put data into sqlite database.
        
            # Sleep a bit before asking the readers again.
            time.sleep(.1)

    # Let's be tidy and join the threads we've started.
    try:
        db.close()
    except:
        pass

    stdout_reader.join()
    stderr_reader.join()

    # Close subprocess' file descriptors.
    process.stdout.close()
    process.stderr.close()

if __name__ == '__main__':
    db = initDatabase(sq, DB_FILE)
    startSubProcess(RTL433, db)
    print("Closing down")
