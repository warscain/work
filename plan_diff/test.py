#!/usr/bin/env python
# -*- coding: utf-8 -*-

import commands

for i in range(0, 1000):
    print commands.getstatusoutput('virsh list')






