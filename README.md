# RaspberryPi Temperature Monitoring
Tested on RaspberryPi 4B

# Requirements
* `sudo apt install python3`
* `sudo apt install -y python3-pip`
* `sudo pip3 install python-dotenv`

# Installation
1. Create folder `sudo mkdir -p /opt/scripts/` and change to it
2. `sudo git clone https://github.com/pthoelken/pi-temperature-monitoring.git`
3. `sudo chmod +x -R /opt/scripts/pi-temperature-monitoring`
4. Initial run `sudo python3 /opt/scripts/pi-temperature-monitoring/pi-temperature-monitoring.py`
* The script will be inform you to fill out the .env file with your credential informations
5. You can run this script again now.
6. Create a cronjob
* `sudo nano /etc/crontab`
* Insert `*/30 * * * *    root    python3 /opt/scripts/pi-temperature-monitoring/pi-temperature-monitoring.py` in the end of the file
* Close file and restart cron service `sudo systemctl restart cron`