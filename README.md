# MMS Grade Monitor
Program I made a long time ago to detect when new feedback and grades are uploaded to MMS. Was written before Microsoft login and 2FA was added so re-authorising after sessions expire isn't supported.

**Fill out config.json:**
* sessionCookie - your JSESSIONID cookie
* courseworks_to_monitor - the name of the courseworks to monitor 
![Example](https://raw.githubusercontent.com/ben-sb/mms-grade-checker/master/images/example-coursework-name.png)
* refresh_time - how often to check for new grades (in seconds)


**Run main.py**
