#!/usr/bin/env python3

import boto3
import datetime
import getpass
import random
from configparser import ConfigParser
from os import path

SESSION_DURATION = 3600


def get_config_profiles():
    config = ConfigParser()
    config.read([path.join(path.expanduser("~"), ".aws/config")])
    sections = []
    for section in config.sections():
        sections.append(section.split(" ")[-1])
    return sections


def role_arn_to_session(aws_profile):
    config = ConfigParser()
    config.read([path.join(path.expanduser("~"), ".aws/config")])
    role_arn = config.get("profile {aws_profile}".format(aws_profile=aws_profile), "role_arn")
    mfa_serial = config.get("profile {aws_profile}".format(aws_profile=aws_profile), "mfa_serial")
    mfa_user = mfa_serial.split("/")[1] + "_" + str(random.randrange(1000, 9999))
    client = boto3.client("sts")
    response = client.assume_role(
        RoleArn=role_arn,
        RoleSessionName=mfa_user,
        SerialNumber=mfa_serial,
        DurationSeconds=SESSION_DURATION,
        TokenCode=getpass.getpass("MFA Token: "),
    )
    time_now = datetime.datetime.now()
    expiry_time = time_now + datetime.timedelta(seconds=SESSION_DURATION)
    fp = open(path.expanduser("~/.aws/session.tmp"), "w")
    fp.write(
        """
## Source this file or copy the below into your terminal to export your temporary credentials

export AWS_ACCESS_KEY_ID={access_key_id}
export AWS_SECRET_ACCESS_KEY={secret_access_key}
export AWS_SESSION_TOKEN={session_token}
export TEXAS_PROFILE={profile}
export TEXAS_SESSION_EXPIRY_TIME={expiry_time}

    """.format(
            access_key_id=str(response["Credentials"]["AccessKeyId"]),
            secret_access_key=str(response["Credentials"]["SecretAccessKey"]),
            session_token=str(response["Credentials"]["SessionToken"]),
            profile=str(aws_profile),
            expiry_time=expiry_time.strftime("%Y%m%d%H%M%S"),
        )
    )
    fp.close()


if __name__ == "__main__":
    sections = get_config_profiles()
    count = 0
    print("\n# Select a profile by entering a number:\n")
    for name in sections:
        print("{count} - Profile: {name}".format(count=count, name=name))
        count += 1
    aws_profile = int(input("Profile number: "))
    role_arn_to_session(sections[aws_profile])
