# openstack-testdrive-config

In the ravello directory you'll find ansible playbooks to configure the OpenStack Test Drive environment, as well as a tool to automatically generate an inventory file from published Ravello applications.

## Pre-requisites

1. python-pip and python-virtualenv packages
1. Python SDK for the Ravello API
1. git package
1. openstack-testdrive-config repository contents (aka this repository)

## Getting pre-requisites

### python-pip and python-virtutalenv packages

**Fedora**

Simply install the python-pip RPM.

```
$ su -c 'dnf install python-pip python-virtualenv'
```

**RHEL 7**

At least rhel-7-server-rpms and EPEL repository should be enabled in the system.

```
$ su -c 'rpm -Uvh http://download.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-10.noarch.rpm'
$ su -c 'yum install python2-pip python-virtualenv'
```

### Python SDK for the Ravello API

Recommed to install it using virtualenv as a regular user, as explained below:

```
$ virtualenv --system-site-packages ~/ravello-sdk
$ source ~/ravello-sdk/bin/activate
$ pip install ravello-sdk
```

### git package

Install git package.

**Fedora**

```
$ su -c 'dnf install git'
```

**RHEL 7**

```
$ su -c 'yum install git'
```

### openstack-testdrive-config repository contents

Clone the openstack-testdrive-config repository to the desired location, as a regular user.

```
$ cd ~
$ git clone https://github.com/vagnerfarias/openstack-testdrive-config.git
```

