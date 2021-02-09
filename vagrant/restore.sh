#!/bin/bash

set -xe

for vm in 192.168.50.50;
do
	vagrant snapshot restore $vm $vm
done
