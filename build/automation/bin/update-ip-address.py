import sys
from json import dumps, loads
from os import getenv
from urllib.request import urlopen

from boto3 import client


def get_ip_address() -> str:
    # For documentation on ipify see here - https://www.ipify.org/
    return urlopen("https://api.ipify.org").read().decode("utf8")


def get_username():
    username = " ".join(sys.argv[1:])
    if username != "":
        return username
    else:
        print("No username provided")
        exit(2)


def update_secret():
    username = get_username()
    ip_address = get_ip_address()
    sm = client("secretsmanager")
    response = sm.get_secret_value(SecretId=getenv("IP_SECRET"))
    secret = response["SecretString"]
    ip_allowlist = loads(secret)
    ip_allowlist[username] = ip_address
    sm.put_secret_value(SecretId=getenv("IP_SECRET"), SecretString=dumps(ip_allowlist))
    print(f'Updated {getenv("PROFILE")} secret with "{username}": "{ip_address}"')


if __name__ == "__main__":
    update_secret()
