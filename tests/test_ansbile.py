TOPOLOGY = """
#         +-------------+
#         |             |
#         |             |
#         | OpenSwitch 1|
#         |             |
#         |             |
#         |             |
#         +------+------+
#                |1
#                |
#                |1
#         +------+------+
#         |             |
#         |             |
#         |  Host 1     |
#         | (control    |
#         |  machine)   |
#         +-------------+
#
# Nodes
[type=openswitch name="OpenSwitch 1"] ops1
[type=host name="Host 1" image="openswitch/ansible:latest"] hs1
[force_name=eth0]ops1:1
#
# Links
hs1:1 -- ops1:1
"""


HS1_IP_MASK = '10.10.10.1/24'
OPS1_IP_MASK = '10.10.10.2/24'
HS1_IP = '10.10.10.1'
OPS1_IP = '10.10.10.2'
PINGCNT = 2
PINGINT = 0.1


def test_topology(topology, step):
    ops1 = topology.get('ops1')
    hs1 = topology.get('hs1')

    assert ops1 is not None
    assert hs1 is not None

    # configure IP on host
    hs1.libs.ip.interface('1', addr=HS1_IP_MASK, up=True)

    # configure IP on switch for interface 1
    with ops1.libs.vtysh.ConfigInterface('1') as ctx:
        ctx.ip_address(OPS1_IP_MASK)
        ctx.no_shutdown()

    # Check the connectivity with host
    ping = hs1.libs.ping.ping(PINGCNT, OPS1_IP, PINGINT)
    assert ping['transmitted'] == ping['received'] == PINGCNT
