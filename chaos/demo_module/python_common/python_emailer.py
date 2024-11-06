import smtplib
import os
import sys
from jinja2 import Environment, FileSystemLoader, Template
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

class CustomEmailer():

    def __init__(self):
        self.to_email = ''
        self.from_email = 'automated-report@mhhc.org'
        self.subject = ''
        self.body_text = ''
        self.body_html = ''

        self.data = dict()
        self.template_path = ''

        self.server = 'smtp.office365.com'
        self.username = 'automated-report@mhhc.org'
        self.password = '@85Burnside'

    # https://aventistech.com/2016/03/07/python-send-email-via-office-365-tls/
    def render_template(self, filename, data):
        ''' renders a Jinja template into HTML '''
        template = Template(open(filename, mode="r", encoding="utf-8").read())
        html = template.render(data)
        return html

    def send(self, to='', subject='', body=''):   

        if to != '':
            self.to_email = to

        if subject !=  '':
            self.subject = subject
        
        if body !=  '':
            self.body_html = body

        # Get Template if exists         
        if len(self.template_path) > 0 and len(self.data) > 0: 
            self.body_html = self.render_template(self.template_path, self.data)
            self.body_text = 'Email Message'
        else:
            # If no text body make empty string
            if len(self.body_text) == 0:
                self.body_text = 'Email Message'

            # If not html, copy from text
            if len(self.body_html) == 0:
                self.body_html = '<html><body>' + self.body_text + '</body></html>'


        msg = MIMEMultipart('Alternative')
        msg['Subject'] = self.subject
        msg['From']    = self.from_email
        msg['To']      = self.to_email
    
        text_content = 'This email has not displayed correctly. Please contact dacolon@mhhc.org for assistance.'
        html_content = self.body_html

        #print(self.body_html)

        part1 = MIMEText(text_content,'plain')
        part2 = MIMEText(html_content,'html')
        
        msg.attach(part1)
        msg.attach(part2)

        mailserver = smtplib.SMTP(self.server,587)
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.ehlo()

        try:
            mailserver.login(self.username, self.password)
        except Exception as e:
            print('Login Error: ' + str(e))
        else:
            try:
                mailserver.sendmail(msg['From'], msg['to'], msg.as_string())
            except Exception as e:
                print('Send Error: ' + str(e))
        finally:
            mailserver.quit()
