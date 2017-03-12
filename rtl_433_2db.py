# A script that runs rtl_433 and logs the json results to an sqlite database.
# 
# Based on the script by jcarduino available at:
# https://github/jcarduino/rtl_433_2db
# 
# Modifications Copyright 2017 Ciarán Mooney

#! /usr/bin/python3
# import sys

import subprocess
import time
import threading
import Queue
import sqlite3
import json

# BEGIN CONFIG
DB_FILE = "/var/lib/temperaturedb/tempdb.sqlite"
# END CONFIG

class asyncFileReader(threading.Thread):
    '''
    Helper class to implement asynchronous reading of a file
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
        '''The body of the tread: read lines and put them on the queue.'''
        for line in iter(self._fd.readline, ''):
            self._queue.put(line)

    def eof(self):
        '''Check whether there is no more content to expect.'''
        return not self.is_alive() and self._queue.empty()

def replace(string):
    ''' Replaces '  ' with ' ' in a string. 
    '''
    while '  ' in string:
        string = string.replace('  ', ' ')
    return string

def initDatabase(db_file):
    ''' Initialise database with the filelocation, db_file. If no database is
        present, then try and create it.

        Database Schema
        ---
        xxx
    '''
    try:
        print("Connecting to database")
        cnx = mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exists, please create it before using this script.")
            print("Tables can be created by the script.")
        else:
            print(err)
    reconnectdb=0#if 0 then no error or need ro be reconnected
    #else:
    #cnx.close()
    cursor = cnx.cursor()
    TABLES = {}
    TABLES['SensorData'] = (
        "CREATE TABLE `SensorData` ("
        "  `sensor_id` INT UNSIGNED NOT NULL,"
        "  `whatdata` varchar(50) NOT NULL,"
        "  `data` float NOT NULL,"
        "  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        ") ENGINE =InnoDB DEFAULT CHARSET=latin1")
    for name, ddl in TABLES.iteritems():
        try:
            print("Checking table {}: ".format(name))
            cursor.execute(ddl)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("Table seams to exist, no need to create it.")
            else:
                print(err.msg)
        else:
            print("OK")
    add_sensordata= ("INSERT INTO SensorData "
                     "(sensor_id, whatdata, data) "
                     "VALUES (%s, %s, %s)")

def startSubProcess(command, db_location):
    '''
    Example of how to consume standard output and standard error of
    a subprocess asynchronously without risk on deadlocking.
    '''
    print "\n\nStarting sub process " + command + "\n"
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
    
    db = initDatabase(db_location)

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
                # put data into sqlite database.
        
            # Sleep a bit before asking the readers again.
            time.sleep(.1)

    # Let's be tidy and join the threads we've started.
    try:
        cursor.close()
        cnx.close()
    except:
        pass
    stdout_reader.join()
    stderr_reader.join()

    # Close subprocess' file descriptors.
    process.stdout.close()
    process.stderr.close()

if __name__ == '__main__':

    startSubProcess("./rtl_433 -R 39 -F json", db_file)
    print("Closing down")
