#!/usr/bin/env python3

import boto3
import os
import sys
from prettytable import PrettyTable


class SSMManager:

    region = None
    client = None
    ssm_client = None
    instances = None
    session = None

    def __init__(self, region):
        self.region = region
        self._connect()

    def _connect(self):
        self.session = boto3.Session(region_name=self.region)
        self.client = self.session.client("ec2")
        self.ssm_client = self.session.client("ssm")

    def get_instances(self):
        filters = [{"Name": "instance-state-code", "Values": ["16"]}]
        self.instances = self.client.describe_instances(Filters=filters)["Reservations"]

    def _get_tag_value_by_name(self, name, tags):
        for i in tags:
            if i["Key"] == name:
                return i["Value"]

    def pretty_print(self):
        self.get_instances()

        inst_list = []
        for instance in self.instances:
            d = dict()
            d["name"] = self._get_tag_value_by_name("Name", instance["Instances"][0]["Tags"])
            d["id"] = instance["Instances"][0]["InstanceId"]
            d["class"] = instance["Instances"][0]["InstanceType"]
            d["pri_ip"] = instance["Instances"][0]["PrivateIpAddress"]
            d["az"] = instance["Instances"][0]["Placement"]["AvailabilityZone"]
            inst_list.append(d)

        sorted_list = sorted(inst_list, key=lambda k: k["name"])

        table = PrettyTable(["Index", "Name", "ID", "Class", "Private IP", "AZ"])
        c = 0
        for i in sorted_list:
            table.add_row([c, i["name"], i["id"], i["class"], i["pri_ip"], i["az"]])
            c += 1

        print(table)

        index = input("Please select an Index to connect to: ")
        return sorted_list[int(index)]

    def connect(self, instance):
        print(
            f"""
        ########################################
        #
        # Connecting to...
        #
        # Instance Id: {instance['id']}
        # Name: {instance['name']}
        # Private IP: {instance['pri_ip']}
        # Class: {instance['class']}
        # Avail Zone: {instance['az']}
        ########################################
            """.format(
                instance
            )
        )

        os.system(f'aws ssm start-session --target {instance["id"]}')


if __name__ == "__main__":

    region = None
    try:
        region = sys.argv[1]
    except IndexError:
        region = input("\nWhich region (default: eu-west-2): ")
        if region == "":
            region = "eu-west-2"

    conn = SSMManager(region=region)
    instance = conn.pretty_print()
    conn.connect(instance)
