# coding=utf-8
import os
import sys
import smtplib
import socket
from email.mime.text import MIMEText
from dotenv import load_dotenv
from pathlib import Path

dotenv_filePath = '.env'
dotenv_tplPath = '.env.tpl'
bln_critical = False

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

config_filePath = os.path.join(application_path, dotenv_filePath)
config_tplPath = os.path.join(application_path, dotenv_tplPath)

if os.path.isfile(config_filePath):    
    load_dotenv(dotenv_path=config_filePath)
    CHECK_FILLED = os.getenv('ENV_CHECK_FILLED')
    CORRECT_VALUE = 'True'

    if CHECK_FILLED == CORRECT_VALUE:
        load_dotenv(dotenv_path=config_filePath)
        MAIL_SERVER = os.getenv('ENV_MAIL_SERVER')
        MAIL_SERVER_PORT = (int(os.getenv('ENV_MAIL_SERVER_PORT')))
        MAIL_SERVER_USERNAME = os.getenv('ENV_MAIL_SERVER_USERNAME')
        MAIL_SERVER_PASSWORD = os.getenv('ENV_MAIL_SERVER_PASSWORD')
        MAIL_SENDER_ADDRESS = os.getenv('ENV_MAIL_SENDER_ADDRESS')
        RECIPIENT_TO = os.getenv('ENV_RECIPIENT_TO')
        RECIPIENT_CC = os.getenv('ENV_RECIPIENT_CC')
        TEMP_HIGH = (float(os.getenv('ENV_TEMP_HIGH')))
        TEMP_CRITICAL = (float(os.getenv('ENV_TEMP_CRITICAL')))
    else:
        print('Please fill out the .env file with your values and check the variable CHECK_FILLED as well. If you have all filled, change CHECK_FILLED to True')
        quit()
else:
    print (config_filePath +  "file not found. We're convert the template from .env.tpl to .env in your application directory. Check out the variables and fill it with your informations. End of file and all is filled, change CHECK_FILLED to True.")
    os.rename(config_tplPath, config_filePath)
    quit()

# At First we have to get the current CPU-Temperature with this defined function
def getcputemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return res.replace("temp=", "").replace("'C\n", "")

# Convert value in float and combine the float and the string after
flt_temp = float(getcputemperature())
str_finaltemp = str(flt_temp) + ' ??C'

# Define other values for message body informations about the pi
str_localhostname = str(socket.gethostname())
str_ipaddr = str(
    (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [
        [(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in
         [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])

## Determine uptime and last boot time
stream_uptime = os.popen('uptime')
stream_boottime = os.popen('uptime -s')
str_boottime = str(stream_boottime.read())
str_uptime = str(stream_uptime.read())

## Determine last installed kernel realese verion
stream_kernelversion = os.popen('uname -a')
str_kernelversion = str(stream_kernelversion.read()) 

# Check if the temperature is above 60??C (you can change this value, but it shouldn't be above 70)
if flt_temp > TEMP_HIGH:
    if flt_temp > TEMP_CRITICAL:
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

        str_mailbodypreparewarning = ('Warning! The actual temperature from your RaspberryPi is: ' + str_finaltemp +
                                      '\n\nIP Address: ' + str_ipaddr +
                                      '\nHostname: ' + str_localhostname +
                                      '\n\nSystem Uptime: ' + str_uptime +
                                      '\nBoot Time: ' + str_boottime +
                                      '\nKernel Version: ' + str_kernelversion
                                      )

        str_mailsubject = "Warning! Temperature: {}".format(str_finaltemp) + " at " + str_localhostname
        str_mailbody = str_mailbodypreparewarning

    # Enter your smtp Server-Connection
    obj_mailserver = smtplib.SMTP(MAIL_SERVER, MAIL_SERVER_PORT)
    obj_mailserver.ehlo()
    obj_mailserver.starttls()
    obj_mailserver.ehlo()
    obj_mailserver.login(MAIL_SERVER_USERNAME, MAIL_SERVER_PASSWORD)

    # Prepare the Message for sending the Mail
    obj_message = MIMEText(str_mailbody)
    obj_sender = MAIL_SENDER_ADDRESS
    ary_recipients = [RECIPIENT_TO, RECIPIENT_CC]
    obj_message['Subject'] = str_mailsubject
    obj_message['From'] = MAIL_SENDER_ADDRESS
    obj_message['To'] = ", ".join(ary_recipients)

    # Finally send the mail
    obj_mailserver.sendmail(obj_sender, ary_recipients, obj_message.as_string())
    obj_mailserver.quit()

    # Critical, shut down the pi
    if bln_critical:
        os.popen('sudo shutdown -h now')
