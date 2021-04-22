#! /usr/bin/python3

import email
import os
import requests

from imaplib import IMAP4_SSL
from dotenv import load_dotenv


def login(EMAIL, PASSWORD):
    email_server = IMAP4_SSL('imap.gmail.com')
    email_server.login(EMAIL, PASSWORD)
    print("Logged in.")
    return email_server


def select_mailbox(email_server, mailbox):
    status, response = email_server.select(mailbox)
    if "OK" in status:
        print(f"{mailbox} selected.")
        return email_server
    else:
        print(f"Failed to select {mailbox}.")


def fetch_new_mail(mail):
    print("Trying to fetch new unread emails.")
    status, response = mail.search(None, '(UNSEEN)')

    email_queue = []
    if 'OK' in status:
        emails = response[0].decode().split()
        if emails:
            for num in emails:
                fetch_status, data = mail.fetch(num, '(RFC822)')
                if 'OK' in fetch_status:
                    msg = email.message_from_string(data[0][1].decode())
                    email_queue.append(
                        {
                            "date": msg['Date'],
                            "from": msg['From'],
                            "subject": ['Subject'],
                            "body": "".join(
                                [part.get_payload() for part in msg.walk()][1]
                            ).replace("\r", "").replace("\n", " ")
                        })
        else:
            print("No new unread emails.")
    return email_queue


def close(email_server):
    print("Logging out.")
    email_server.close()
    email_server.logout()
    print("Logged out.")


if __name__ == "__main__":
    load_dotenv()
    server = login(os.environ.get("EMAIL"), os.environ.get("PASSWORD"))
    mailbox = select_mailbox(server, "INBOX")
    try:
        emails = fetch_new_mail(mailbox)
    except IndexError:
        emails = fetch_new_mail(mailbox)

    if emails:
        for mail in emails:
            FROM1 = os.environ.get("FROM1")
            FROM2 = os.environ.get("FROM2")
            SUBJECT1 = os.environ.get("SUBJECT1")
            SUBJECT2 = os.environ.get("SUBJECT2")
            SUBJECT3 = os.environ.get("SUBJECT3")
            if FROM1 in mail['from'] or FROM2 in mail['from'] or \
                                        SUBJECT1 in mail['subject'] or \
                                        SUBJECT2 in mail['subject'] or \
                                        SUBJECT3 in mail['subject']:
                print("Email found!")
                print(mail)
                print()

                params = {
                    "access_token": os.environ.get("ACCESS_TOKEN"),
                    "secret_token": os.environ.get("SECRET_TOKEN"),
                    "monkey": os.environ.get("MONKEY"),
                    "announcement": os.environ.get("ANNOUNCEMENT"),
                }
                requests.get('https://api.voicemonkey.io/trigger', params=params)
        close(server)

    print("Request sent.")
