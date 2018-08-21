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
* RTL_433 - commit 7d558b770a11c5af5d9c231755a6bcf1fb2059e9
* fstab - must mount USB drive during boot. If no specific mount point
defined in fstab, the program is run by Cron before USB disks mounted. fstab
example
UUID=f3e278c2-1043-4d4c-9440-e761d0a3aa77       /media/piDrive  ext4    defaults          0       0
* Crontab line
 @reboot     root    /opt/start_logger.py
* rtl_433 Install location /opt/
* rtl_433_2db.py Install location /opt/
* start_logger.py install location /opt/
* SQlite location
/media/piDrive/db/temperature_sensor/temperaturedb.sqlite
* SQlite database owner, pi 
sudo chown pi:pi
