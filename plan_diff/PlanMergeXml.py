#!/usr/bin/env python
# -*- coding: utf-8 *-*

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import re

doc = open('/home/lucifer/Downloads/tcms-testcases-2013-01-27.xml').read()
soup = BeautifulStoneSoup(doc)

print soup.prettify()
print '=' * 100

print soup.contents[0].contents[0]

