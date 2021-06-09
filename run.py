#!/usr/bin/env python3

import json
import datetime
import urllib.request
import time
import smtplib
import ssl
from email.mime.text import MIMEText
import sys
import configparser
import os.path

clinics = [
    {"name": "Hallsberg", "code": 1350, "slots": 0},
    {"name": "Karlskoga", "code": 1349, "slots": 0},
    {"name": "Lindesberg", "code": 1348, "slots": 0},
    {"name": "Örebro Bolundsängen", "code": 1351, "slots": 0},
    {"name": "Örebro Conventum", "code": 1352, "slots": 0}
]


def check_times():

    appointment_type = 11941  # Vaccin dos 1?

    today = datetime.date.today()

    start_date = today.strftime("%y%m%d")
    stop_date = (today + datetime.timedelta(weeks=2)).strftime("%y%m%d")

    base_url = "https://booking-api.mittvaccin.se/clinique/{}/appointments/{}/slots/{}-{}"

    any_time = False

    any_new_time = False

    output = ""

    file_exists = os.path.isfile("data.csv")

    with open("data.csv", "a", encoding="utf-8") as log_file:
        if not file_exists:
            log_file.write('\ufeff')
            log_file.write("Timestamp")
            for clinic in clinics:
                log_file.write(",{}".format(clinic["name"]))
            log_file.write("\n")

        log_file.write("\n{}".format(
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        for index, clinic in enumerate(clinics):

            url = base_url.format(
                clinic["code"], appointment_type, start_date, stop_date)

            available = 0

            with urllib.request.urlopen(url) as req:

                data = json.loads(req.read())
                for item in data:
                    date = item["date"]
                    for slot in item["slots"]:
                        if slot.get("available") == True:
                            available += 1
                            print("Tid finns {} klockan {}\n".format(
                                date, slot["when"]))
            if available > 0:
                any_time = True

            if available > clinic["slots"]:
                any_new_time = True
            clinics[index]["slots"] = available

            log_file.write(",{}".format(available))

            out_template = "{} tider lediga på {} \n\n"
            output += (out_template.format(available,
                                           "<a href=\"https://bokning.mittvaccin.se/klinik/{}/bokning\">{}</a>".format(clinic["code"], clinic["name"])))
            print(out_template.format(available, clinic["name"]))

    return [any_time, any_new_time, output]


def send_email(message: str, config):

    sender = config['smtp']["user"]
    receivers = config['receivers']['list'].split(",")
    body_of_email = message.replace("\n", "<br/>")

    msg = MIMEText(body_of_email, "html")
    msg['Subject'] = 'Vaccinationstider'
    msg['From'] = sender
    msg['To'] = ','.join(receivers)

    s = smtplib.SMTP_SSL(host='smtp.gmail.com', port=465)
    s.login(user=config['smtp']["user"], password=config['smtp']["password"])
    s.sendmail(sender, receivers, msg.as_string())
    s.quit()


def pretty_sleep(seconds: int):
    elapsed = 0
    loop_time = 5
    while elapsed < seconds:
        time.sleep(loop_time)
        sys.stdout.write(".")
        sys.stdout.flush()
        elapsed += loop_time


def run(config):
    while datetime.datetime.now().minute not in {0, 15, 30, 45}:
        pretty_sleep(30)

    def task():
        print("")
        [any_time, any_new_time, output] = check_times()
        if any_new_time:
            send_email(output, config)

    while True:
        task()
        pretty_sleep(15 * 60)


dirname = os.path.dirname(__file__)
config = configparser.ConfigParser()
config.read(os.path.join(dirname, 'config.ini'))

run(config)
