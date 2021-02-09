#!/bin/bash
vagrant up --provision --provider virtualbox
vagrant ssh-config >> ~/.ssh/config
