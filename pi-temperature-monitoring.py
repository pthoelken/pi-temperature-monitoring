# coding=utf-8
import os
import smtplib
import socket
from email.mime.text import MIMEText

# Define temperatures for warnings and shutdown command
bln_critical = False
int_high = 60
int_criticalhigh = 70

## Mail Server Configurations
str_mailserver = "foobar.fqdn.com"
int_mailserverport = 25

str_mailsenderaddr = "alertfrompi@foobar.fqdn.com"
str_firstreciepient = "sysadmin01@foobar.fqdn.com"
str_secreceiepient = "sysadmin02@foobar.fqdn.com"


# At First we have to get the current CPU-Temperature with this defined function
def getcputemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return res.replace("temp=", "").replace("'C\n", "")


# Convert value in float and combine the float and the string after
flt_temp = float(getcputemperature())
str_finaltemp = str(flt_temp) + ' °C'

# Define other values for message body informations about the pi
str_localhostname = str(socket.gethostname())
str_ipaddr = str(
    (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [
        [(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in
         [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])

## Determine uptime and last boot time
stream_uptime = os.popen('python -m uptime')
stream_boottime = os.popen('python -m uptime -b')
str_boottime = str(stream_boottime.read())
str_uptime = str(stream_uptime.read())

## Determine last installed kernel realese verion
stream_kernelversion = os.popen('uname -a')
str_kernelversion = str(stream_kernelversion.read()) 

# Check if the temperature is above 60°C (you can change this value, but it shouldn't be above 70)
if flt_temp > int_high:
    if flt_temp > int_criticalhigh:
        bln_critical = True

        str_mailbodypreparecirtical = ('Critical! Pi is shutting down at actual temperature of: ' + str_finaltemp +
                                       '\n\nIP Address: ' + str_ipaddr +
                                       '\nHostname: ' + str_localhostname +
                                       '\n\nSystem Uptime: ' + str_uptime +
                                       '\nBoot Time: ' + str_boottime +
                                       '\nKernel Version: ' + str_kernelversion
                                       )

        str_mailsubject = "Critical! Temperature is: {}".format(str_finaltemp) + " at " + str_localhostname + " is shutting down!!"
        str_mailbody = str_mailbodypreparecirtical
    else:

        str_mailbodypreparewarning = ('Warning! PoE Fan is running at actual temperature of: ' + str_finaltemp +
                                      '\n\nIP Address: ' + str_ipaddr +
                                      '\nHostname: ' + str_localhostname +
                                      '\n\nSystem Uptime: ' + str_uptime +
                                      '\nBoot Time: ' + str_boottime +
                                      '\nKernel Version: ' + str_kernelversion
                                      )

        str_mailsubject = "Warning! Temperature: {}".format(str_finaltemp) + " at " + str_localhostname
        str_mailbody = str_mailbodypreparewarning

    # Enter your smtp Server-Connection
    obj_mailserver = smtplib.SMTP(str_mailserver, int_mailserverport)
    obj_mailserver.ehlo()

    # Prepare the Message for sending the Mail
    obj_message = MIMEText(str_mailbody)
    obj_sender = str_mailsenderaddr
    ary_recipients = [str_firstreciepient, str_secreceiepient]
    obj_message['Subject'] = str_mailsubject
    obj_message['From'] = str_mailsenderaddr
    obj_message['To'] = ", ".join(ary_recipients)

    # Finally send the mail
    obj_mailserver.sendmail(obj_sender, ary_recipients, obj_message.as_string())
    obj_mailserver.quit()

    # Critical, shut down the pi
    if bln_critical:
        os.popen('sudo shutdown -h now')