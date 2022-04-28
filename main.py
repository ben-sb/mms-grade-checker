from classes.mms import MMS_Monitor
import json

if __name__ == '__main__':
    try:
        config = json.load(open('config.json'))
        mms_monitor = MMS_Monitor(config['sessionCookie'], config['courseworksToMonitor'], config['refreshTime'])
        mms_monitor.run()
    except KeyError:
        print('Wrongly formatted config file')
    except FileNotFoundError:
        print("Config file not found")
    except Exception as e:
        print("Exception: " + str(e))
