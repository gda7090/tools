#-*- coding: utf-8 -*-
"""
	Description:
        Mail send
"""



from __future__ import (unicode_literals, print_function)
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
try:
    import regex as re
except ImportError:
    import re
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header
import time
from getpass import getuser
import traceback
try:
    from napec._log import mainLog as logger
except ImportError:
    import logging as logger

__all__ = ["sender"]
__author__ = "liuxiaochuan@novogene.com"
__dir__ = os.path.dirname(os.path.realpath(__file__))


class ConfigParse(object):
    def __init__(self):
        from napec.tools import (toUnicode, parse_conf)
        configNow = parse_conf(__dir__+os.sep+"mail.ini")
        self.deputy = configNow["deputys"].get("deputy_account", "liuxiaochuan")
        self.users = dict(configNow["accounts"])
        self.smtp_server = configNow["server-send"]["smtp_server"]
        self.smtp_port = configNow["server-send"]["smtp_port"]

class sender(object):
    """
    Description:{
        email send
    }
    """
    def __init__(self):
        configs = ConfigParse()
        from napec.access import acc_map
        self.deputy = configs.deputy
        self.passwd = configs.users[self.deputy]
        self.server = configs.smtp_server
        self.port = int(configs.smtp_port)
        self.accMap = acc_map()
        self.smtp = smtplib.SMTP_SSL()
        self.smtp.set_debuglevel(0)
    def set(self, deputy, password):
        self.deputy = deputy
        self.passwd = password
        return 0
    def send(self, receivers, title, text, mType="plain", attachments=None):
        """
        Usage:{
            reveivers: to whom the mail sent, separate by ";"
            title:
            content:
        }
        """
        self.smtp.connect(host=self.server, port=self.port)
        self.smtp.login(self.deputy, self.passwd)
        self.smtp.ehlo()
        msg = MIMEMultipart()
        mailTo = []
        for il in receivers.strip(";").split(";"):
            if il.strip().endswith("@novogene.com"):
                mailTo.append(il.strip())
            elif re.search(r"[\u4E00-\u9FEF]", il.strip()):
                mailTo.append(self.accMap.s2m(il.strip(), fuzzy=True)+"@novogene.com")
            else:
                mailTo.append(self.accMap.c2m(il.strip(), fuzzy=True)+"@novogene.com")
        if attachments != None:
            attach_list = attachments.split(";")
            for il in attach_list:
                afile = MIMEApplication(open(il.strip(),'rb').read())
                afile.add_header("Content-Disposition",'attachment',filename=il.split("/")[-1].strip())
                msg.attach(afile)
        msg['Subject'] = Header(title, "utf-8")
        msg['From'] = 'cancer_info<cancer_info@novogene.com>'
        # mailTo.append("liuxiaochuan@novogene.com")
        msg['To'] = ";".join(mailTo)
        msg.attach(MIMEText(text, mType, 'utf-8'))
        self.smtp.sendmail(self.deputy, mailTo, msg.as_string())
        self.smtp.quit()
        return 0
    def trySend(self, receivers, title, text, mType="plain", attachments=None):
        try:
            self.send(receivers, title, text, mType, attachments)
            logger.info('Mail #Subject<{}> successfully sent to #receiver<{}> by #user<{}> with #deputy<{}>'.format(\
                    title, receivers, getuser(), self.deputy))
        except Exception:
            fmt_err = traceback.format_exc()
            logger.error('MailSendFailed: Mail #Subject<{}> failed to send to #receiver<{}> by #user<{}> with #deputy<{}>\nError log:\n<{}>'.format(\
                    title, receivers, getuser(), self.deputy, fmt_err))
            return -1
        return 0
    def close(self):
        try:
            self.smtp.close()
        except Exception:
            pass
        return 0

if __name__ == "__main__":
    ss = sender()
    ss.send("liuxiaochuan")
    ss.close()
