# Copyright (C) 2016 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.


TOPOLOGY = """
#         +-------------+
#         |             |
#         |             |
#         | OpenSwitch1 |
#         |             |
#         |             |
#         |             |
#         +------+------+
#                |sp1
#                |
#                |eth0
#         +------+------+
#         |             |
#         |             |
#         |  Host1      |
#         | (control    |
#         |  machine)   |
#         +-------------+
#
# Nodes
[type=openswitch name="OpenSwitch1"] ops1
[type=oobmhost name="Host1" image="openswitch/ansiblecm:latest"] hs1
#
# Links
[force_name=oobm] ops1:sp1
ops1:sp1 -- hs1:eth0
"""


HOSTIP = '192.168.1.2/24'
OPSIP = '192.168.1.3/24'
PINGCNT = 4


def set_switch_config(ops1, step):
    step("Configure switch interface mgmt IP address")
    with ops1.libs.vtysh.ConfigInterfaceMgmt() as ctx:
        ctx.ip_static(OPSIP)


def set_host_config(hs1, step):
    step("Configure host interface")
    hs1.libs.ip.interface('eth0', addr=HOSTIP, up=True)


def ping(ops1, hs1, pingcnt, step):
    step("Test ping between switch and host")
    '''
    first ping is to make sure we have ARP entries and then run
    assert on the second ping for connection check so that
    there is no packet loss
    If this ping fails, there is no point running the other tests
    as there is no reachability
    '''
    ping = hs1.libs.ping.ping(pingcnt, OPSIP.split('/')[0])
    ping = hs1.libs.ping.ping(pingcnt, OPSIP.split('/')[0])
    assert ping['received'] == pingcnt, (
        "Total of received packets is equal to 0, " +
        "Expected: %d" % (pingcnt)
    )
    step("Ping from control machine to OPS successful!!!")


def host_ansbile_defaults(hs1, step):
    step("Add default values to ansible.cfg and hosts file")
    hs1("echo \"[defaults]\n"
        "inventory=/etc/ansible/hosts\n"
        "host_key_checking = False\" > /etc/ansible/ansible.cfg")

    """ Add IP of the switch to the host file on the control machine """
    hs1("echo \"[ops]\n\%s ansible_ssh_port=22\" > /etc/ansible/hosts"
        % (OPSIP.split('/')[0]))

    """ Run the shell script to export ansible variable,
        ANSIBLE_SCP_IF_SSH=y """
    hs1(". env_ansible.sh")


def host_ssh_config(hs1, step):
    step("Generating and adding the ssh key identity on the host")
    """ generate ssh key """
    hs1("ssh-keygen -t rsa -f /root/.ssh/id_rsa -N ''")

    """ start the ssh agent """
    hs1("eval `ssh-agent -s`")

    """ Add the identity """
    hs1("ssh-add /root/.ssh/id_rsa")


def copy_ssh_key_ansible(hs1, step):
    """ run playbook to copy ssh key to authorized keys in switch """
    step("\nRunning the playbook on the openswitch to copy ssh key\n")
    out = hs1("ansible-playbook /ansible/copy_public_key.yml -u root")
    assert "unreachable=0" in out, \
           "Could not reach the Openswitch - Failed!!"
    assert "failed=1" not in out, "copying public key to openswitch failed!!"


def ping_ops_ansible(hs1, step):
    """ run ansible ping module in a playbook to check the connectivity """
    step("\nRunning the ansible playbook to ping the opwnswitch\n")
    out = hs1("ansible-playbook /ansible/ping.yml")
    assert "unreachable=0" in out, "Could not reach the Openswitch - Failed!!"
    assert "failed=1" not in out, "Ping to Openswitch failed!!"
    step("\n\n#Successfully Copied ssh key and pinged the OPS using Ansible#")


def test_ansible_copy_ssh_key_playbook(topology, step):
    ops1 = topology.get('ops1')
    hs1 = topology.get('hs1')

    assert ops1 is not None
    assert hs1 is not None

    """ Assign IP to openswitch """
    set_switch_config(ops1, step)

    """ Configure IP to the host """
    set_host_config(hs1, step)

    """ Connectivity test """
    ping(ops1, hs1, PINGCNT, step)

    """ Save default cfg values and hosts """
    host_ansbile_defaults(hs1, step)

    """ generate and add ssh key identity """
    host_ssh_config(hs1, step)

    """ run the ansible playbook to copy ssh key and check
        if we can use ping module from ansible control machine
        to openswitch """
    copy_ssh_key_ansible(hs1, step)

    """ run ansible playbook to ping the openswitch """
    ping_ops_ansible(hs1, step)
