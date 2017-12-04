RTL433 to SQLITE Database Script
---

A python script that runs RTL433 and collects the data into an SQLITE 
database. Specifically, this script takes data from a cheap wireless
thermometer, ready for use in a homemade heating system.

Install
--
Note, these are not exhaustive. They are merely a guide to installing on my
systems. I may flesh these out in future

* Raspberry Pi 3
* Raspbian GNU/Linux 8 (jessie)
* RTL_433 - branch ...01c8c329197d0 (essentially "my version")
* Crontab line
 @reboot     root    /opt/rtl_433_2db.py
* RTL_433 Install location /opt/
* RTL_433_2db Install location /opt/
* SQlite location
/media/pi/MooneyBackup/db/temperature_sensor/temperaturedb.sqlite
