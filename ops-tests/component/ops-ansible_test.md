# Ansible Test Cases

- [Test to copy ssh key using ansible playbook](#test-to-copy-ssh-key-using-ansible-playbook)

## Test to copy ssh key using ansible playbook
### Objective
Verify that ssh key can be copied from control machine to openswitch and
communciation can be established using ping module.

### Requirements
The topology framework test setup is required for this test.

### Setup

#### Topology diagram

```
      +-----------------+             +------------+
      |     Ansible     | eth0   eth0 |            |
      | control machine |-------------| OpenSwitch |
      |    (server)     |             |  (switch)  |
      +-----------------+             +------------+
```

### Description
This test confirms that we can establish ssh communication between Ansible
control machine and the openswitch. We use the ansible playbook to copy
the ssh key from ansible control machine to openswitch and then try
using a ping module through ansible playbook to check if we can communicate
with the openswitch.

#### Steps to run the tests:
- git clone https://git.openswitch.net/openswitch/ops-build  ops-build
- cd ops-build
- make configure genericx86-64
- make devenv\_init
- make devenv\_add ops-ansible
- make testenv\_init
- make testenv\_run component ops-ansible

### Test result criteria
#### Test pass criteria
Running Ansible ping module in an ansible playbook from control machine
on the openswitch succeeds.
#### Test fail criteria
Running Ansible ping module in an ansible playbook fails on the openswitch
