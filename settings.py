import os

TOKEN = os.environ.get("TOKEN")

HOST = 'https://frantbot.herokuapp.com/'

PORT = os.environ.get("PORT") # 443, 80, 88 or 8443 (port need to be 'open')

SSL_CERT = 'https://frantbot.herokussl.com/' # './webhook_cert.pem'  # Path to the ssl certificate

SSL_PRIV = 'https://frantbot.herokussl.com/' # './webhook_pkey.pem'  # Path to the ssl private key
