import sys
from json import dumps, loads
from os import getenv

from boto3 import client


def get_username():
    username = " ".join(sys.argv[1:])
    if username != "":
        return username
    else:
        print("No username provided")
        exit(2)


def update_secret():
    username = get_username()
    sm = client("secretsmanager")
    response = sm.get_secret_value(SecretId=getenv("IP_SECRET"))
    secret = response["SecretString"]
    ip_allowlist = loads(secret)
    del ip_allowlist[username]
    sm.put_secret_value(SecretId=getenv("IP_SECRET"), SecretString=dumps(ip_allowlist))
    print(f'Deleted "{username}" from {getenv("PROFILE")} secret')


if __name__ == "__main__":
    update_secret()
