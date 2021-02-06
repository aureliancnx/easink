import threading
import time

email_queue = []


def queue_start():
    thread1 = MailQueue(40, "Thread-1MailQueue", 2)

    # Start new Threads
    thread1.start()


def send_mail(mail_object):
    email_queue.append(mail_object)


class MailQueue(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        while True:
            if len(email_queue) > 0:
                email = email_queue[0]
                print("Email found in queue: {0}".format(email.subject))
                email.send()
                email_queue.remove(email)
            time.sleep(5)