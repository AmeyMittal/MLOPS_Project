#!/bin/bash
# This script creates an object storage container using OpenStack CLI

#switch to CHI@TACC auth environment
source ~/chi/CHI@TACC-openrc.sh

# Create the container
openstack container create object-storage-project48

echo "Created object store container: object-storage-project48"