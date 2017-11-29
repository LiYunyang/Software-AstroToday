# -*- coding:utf-8 -*-
import smtplib
import time
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr


def send(receiver, f, date):
    def _format_addr (s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr.encode('utf-8') if isinstance(addr, unicode) else addr))

    host = 'smtp.163.com'
    port = 25
    sender = 'sagittarius_a@163.com'
    # from_addr = raw_input('From: sagittarius_a@163.com')
    pwd = 'dayday915'


    msg = MIMEMultipart()
    msg['subject'] = u'%sAstroToday' % date
    msg['from'] = _format_addr(u'Sagittarius A<%s>' % sender)
    msg['to'] = receiver
    text = u'Thank you for your subscription! \n\n Any comment or feedback to AstroToday is highly appreciated. \n \n \n Yunyang Li'
    part1 = MIMEText(text, 'plain')
    msg.attach(part1)
    with open(f, "rb") as fil:
        part = MIMEApplication(fil.read(), Name=f)

        part['Content-Disposition'] = 'attachment; filename=AstroToday%s.pdf' % date
        msg.attach(part)

    try:
        s = smtplib.SMTP(host, port)
        s.login(sender, pwd)
        s.sendmail(sender, receiver, msg.as_string())

    except smtplib.SMTPException:
        print 'error'


def getCurTime():
    nowTime = time.localtime()
    year = str(nowTime.tm_year - 2000)
    month = str(nowTime.tm_mon)
    if len(month) < 2:
        month = '0' + month
    day = str(nowTime.tm_mday)
    if len(day) < 2:
        day = '0' + day
    return year + month + day

if __name__ == '__main__':
    date = getCurTime()
    open("../data/%s.pdf" % date, "wb").write(open('arxivdaily.pdf', "rb").read())
    with open('subscribeList.csv', 'r') as lines:
        for line in lines:
            if line[0] != '#':
                if line[:-1] == '\n':
                    line = line[:-1]
                print 'sending to %s' % line
                send(line, '../data/%s.pdf' % date, date)
    print 'email sent'
