import subprocess
import json
from influxdb import InfluxDBClient
import re

#Connect to InfluxDB and drop the old data.

influxdb_ip = '10.1.1.1'
username = 'agent'
password = '@g1nt'
database = 'advertisement'

start = InfluxDBClient(influxdb-ip, 8086, username,password)
start.query('drop database ' + database)
start.query('create database '+ database)
client = InfluxDBClient(influxdb-ip, 8086, username,password, database)

# Juniper MX
# List all files in the directory.
process = subprocess.Popen(['ls', 'adv_juniper'],
stdout=subprocess.PIPE,
stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

file_list = stdout.decode('utf-8').split("\n")
file_list.pop()

#Write data in the database, advetisement.
for file in file_list:
    # Load the output of show route advertising-protocol bgp ___ table ___
    with open("adv_json/"+file) as f:
        data = json.load(f)
    if len(list(data["route-information"][0].keys())) != 0:
        # Get the advertising prefixes.
        prefixes = data["route-information"][0]["route-table"][0]["rt"]
        for each in prefixes:
            #print(each["rt-destination"][0]["data"])
            #print(each["rt-entry"][0]["as-path"][0]["data"])
            prefix=each["rt-destination"][0]["data"]
            aspath=each["rt-entry"][0]["as-path"][0]["data"]

            #Data normalization
            x=aspath.split()
            if "[131618]" in x:
                i = x.index("[131618]")
                x.pop(i)
            elif "[7483]" in x:
                i = x.index("[7483]")
                x.pop(i)

            result = " ".join(x)
            #print(result)
            #Ignore /32 prefix
            #Generate InfulxDB data
            if re.search("/32",prefix):
                continue
            else:
                data = [
                    {
                        "measurement" : prefix,
                        "fields": {
                            "Circuit": file,
                            "AS Prepend": result
                        }
                    }
                ]
                #print(data)
                #Write Data to DB.
                client.write_points(data)
    else:
        continue

#IOS XR
# List all files in the directory.
process = subprocess.Popen(['ls', 'adv_xr'],
stdout=subprocess.PIPE,
stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

file_list = stdout.decode('utf-8').split("\n")
file_list.pop()

#Write data in the database, advetisement.
for file in file_list:
    # Load the output of show bgp neighbor ___ advertised-routes
    with open("adv_xr/"+file) as f:
        x = f.readlines()

    prefix = []
    aspath = []
    #Normalize the output and get only prefix and AS path
    for each in x:
        l = each.strip().split(" ")
        while("" in l):
            l.remove("")
        if 'Aggregate' not in l:
            l.insert(3,'Aggregate')
        prefix.append(l[0])
        aspath.append(" ".join(l[4:]))

    #Ignore empty file
    try:
        prefix.pop(0)
        prefix.pop()
        prefix.pop()

        aspath.pop(0)
        aspath.pop()
        aspath.pop()
    except:
        continue

    #Align with the output of Juniper
    for each in aspath:
        i = aspath.index(each)
        aspath[i] = re.sub ('(.*)(i)',r'\1 I',each)

    d = {}

    #Generate InfulxDB data
    for x in prefix:
        i = prefix.index(x)
        #Ignore /32 prefix
        if re.search("/32",x):
            continue
        else:
            data = [
                {
                    "measurement" : x,
                    "fields": {
                        "Circuit": file,
                        "AS Prepend": aspath[i]
                    }
                }
            ]
            #print(data)
            #Write Data to DB.
            client.write_points(data)
