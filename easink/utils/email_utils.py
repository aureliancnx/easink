import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def sendMail(email, subject, content):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = 'Eas.Ink <motizaurelian@gmail.com>'
    msg['To'] = email

    mimetxt = MIMEText(content, 'html')
    msg.attach(mimetxt)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.connect("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login("motizaurelian@gmail.com", "juucwfowdgkghjjp")

    s.sendmail(msg['From'], email, msg.as_string())
    s.quit()