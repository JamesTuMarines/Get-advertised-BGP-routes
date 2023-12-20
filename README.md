Get BGP advertised routes from Juniper MX and IOS-XR and push them to the remote InfluxDB.

Instruction
---

1. Add devices in the host file called hosts.
2. Change variables in the host_var
~~~
ansible_user: "user" <=== Enter Your username on devices. 
ansible_ssh_pass: "password" Enter <==== Your username on devices.
ansible_connection: "network_cli"
ansible_network_os: "cisco.iosxr.iosxr"
os: "xr"

peers:
  1:  ===> This should be unique when you add the new peer.
    name: lab-A9K-ISP  ===> This name would be the name of your measurement in the InfluxDB
    ip: 192.168.2.1    ===> The BGP Peer IP.
~~~
3. Run the ansible-playbook
~~~
ansible-playbook -i hosts influx_adv.yml
~~~
4. Modify the information of InfluxDB in push_influx.py
~~~
influxdb_ip = '10.1.1.1'
username = 'agent'
password = '@g1nt'
database = 'advertisement'
~~~
5. Install the packages
~~~
pip3 install influxdb
~~~
6. Execute the Python code
~~~
python3 push_influx.py
~~~
