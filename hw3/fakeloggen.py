#!/usr/bin/env python3
import sys
import os
from time import sleep
from datetime import datetime
fake_log = ["{}, ping -r, fatal error, a value must be provided for the option -r.\n",
            "{}, ping -n, fatal error, a value must be provided for the option -n.\n",
            "{}, confj4ing, fatal error, 'confj4ing' is not recognized as an internal or external command, operable program or batch file.\n",
            "{}, confing, fatal error, 'confing' is not recognized as an internal or external command, operable program or batch file.\n",
            "{}, hkiuyrdg, fatal error, 'hkiuyrdg' is not recognized as an internal or external command, operable program or batch file.\n",
            "{}, m,lhfghfdx48478, fatal error, 'm' is not recognized as an internal or external command, operable program or batch file.\n"]

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('no argument')
        sys.exit()

    magic_num = int(sys.argv[1])
    if os.path.exists("/var/log/fakelog.log"): os.remove("/var/log/fakelog.log")
    while magic_num != 1:
        fd = open("/var/log/fakelog.log", "a")
        fd.write(fake_log[magic_num%len(fake_log)].format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        fd.close()
        if(len(sys.argv) == 3 and sys.argv[2] == "--logrotate"): os.system("logrotate /etc/logrotate.d/fakelog")
        magic_num = 3*magic_num+1 if magic_num%2 else magic_num//2
        sleep(0.1)