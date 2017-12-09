#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Starts the RTL_433_2sqlite logger for logging temperature sensor data from
# RTL_433
# Ciarán Mooney 2017

import rtl_433_2sqlite as 2sqlite


# BEGIN CONFIG
DB_FILE = "/tmp/tempdb.sqlite"
RTL433 = "/home/ciaran/Code/rtl_433/build/src/rtl_433"
DEBUG = False
TESTS = "/home/ciaran/Code/rtl_433_tests/"
# END CONFIG

if __name__ == '__main__':
    db = 2sqlite.initDatabase(sq, DB_FILE)
    2sqlite.startSubProcess(RTL433, db, DEBUG)
    print("Closing down")
