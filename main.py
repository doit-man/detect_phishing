import requests
import urllib.parse
from tld import get_tld
import ssl
import socket
import whois
import sys
import datetime
from dateutil.parser import parse
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urlparse
import numpy as np
from sklearn import tree
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

    # 1: 정상 / -1 비정상
def Check_TinyURL(url) :
    response = requests.get(url)
    for resp in response.history:
        if resp.status_code == 301 or resp.status_code ==302:
            return -1
        else:
            return 1

# url 길이 check 1: 정상 / 0: 비정상
def Check_URL_Length(url) :
    if len(url) <54 :
        return 1
    elif len(url) >= 54 and len(url) <= 75:
        return 0
    else :
        return -1

def Check_At_symbol(url) :
    if '@' in url:
        return -1
    else :
        return 1

def Check_double_slash(url) :

    parse = urllib.parse.urlparse(url)
    path = parse.path
    if '//' in path:
        return -1
    else :
        return 1

def Check_Prefix_Suffix(url) :
    if '-' in url:
        return -1
    else :
        return 1

def Check_Sub_Domain(url):
    if "www."in url[:12]:
        url = url.replace("www.","")
    domain = get_tld(url,as_object=True)
    if domain.subdomain =="" :
        return 1
    dot = domain.subdomain.count('.')
    if dot == 0:
        return 0
    else:
        return -1

def Check_SSL_connect(url):
    try:
        context = ssl.create_default_context()
        sck = context.wrap_socket(socket.socket(), server_hostname=url)
        sck.connect((url,443))
    except TimeoutError :
        return 0
    cert=sck.getpeercert()
    issuer = dict(x[0] for x in cert['issuer'])
    issued_by = issuer['organizationName']

    #trusted_issuer_list = get_trusted_issuer()

    return 1
#def get_trusted_issuer() :


def Check_Domain_term(url):
    try :
        domain = whois.whois(url)
        if type(domain.expiration_date) is list:
            expiration_date = domain.expiration_date[0]
        else:
            expiration_date = domain.expiration_date
        if type(domain.updated_date) is list:
            updated_date = domain.updated_date[0]
        else:
            updated_date = domain.updated_date

        total_date = (expiration_date - updated_date).days
    except whois.parser.PywhoisError:
        return -1
    if total_date <= 365:
        return -1
    else:
        return 1
def Check_Favicon(url):
    response = urlopen(url)
    soup = BeautifulSoup(response, 'html.parser')
    tag_link = soup.findAll("link", rel="shortcut icon")
    if not tag_link:
        return -1
    for link in tag_link:
        parse = urlparse(link.get('href'))

        if parse.netloc == '':
            return 1
        else:
            return -1

def Check_port(url):
    domain = whois.whois(url)
    try:
        ip = socket.gethostbyname(domain)
    except:
        return -1
    socket.setdefaulttimeout(2)


    ports = [80, 21, 22, 23, 445, 1433, 1521, 3306, 3389]
    for port in ports:
        s = socket.socket()
        if port == 80:
            try:
                s.connect((ip, port))
            #                 print("%d port is open!" % port)
                s.close()
            except:
            #                 print("%d port is closed!" % port)
                return -1
        else:
            try:
                s.connect((ip, port))
            #                 print("%d port is open!" % port)
                s.close()
                return -1
            except:
            #                 print("%d port is closed!" % port)
                pass

    return 1







training_data = np.genfromtxt('Training Dataset.arff', delimiter=',', dtype=np.int32)

inputs = training_data[:, :-1]
outputs = training_data[:, -1]
training_inputs = inputs[:7000]
training_outputs = outputs[:7000]

testing_inputs = inputs[7000:]
testing_outputs = outputs[7000:]
classifier = tree.DecisionTreeClassifier()

classifier.fit(training_inputs, training_outputs)
predictions = classifier.predict(testing_inputs)
accuracy = 100.0 * accuracy_score(testing_outputs, predictions)

print ("result : " + str(accuracy))