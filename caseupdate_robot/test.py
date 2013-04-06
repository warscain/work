#!/usr/bin/env python
# -*- coding: utf-8 *-*
import re
import urllib
import urllib2
import cookielib
import os

class ChangeLogMark(object):
    def __init__(self, filein, planid):
        self.filein = filein
        self.planid = planid

    def _caseid_list(self, filein):
        fh_filein = open(filein)
        linecmp = re.compile('^([0-9]{6})')
        caseidlist = []
        for line in fh_filein:
            caseid_search = re.search(linecmp, line)
            if caseid_search:
                caseidlist.append(caseid_search.group(1))
        print 'All cases num:', len(caseidlist)
        return caseidlist

    def _case_html_read(self, caseid, planid):
        caseid = str(caseid)
        planid = str(planid)
        #fileout = open('fileout', 'w')
        url = 'https://tcms.engineering.redhat.com/case/' + caseid + '/?from_plan=' + planid
        # this creates a password manager
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, url, 'xxxxx', 'xxxxxx')
        # create the AuthHandler
        authhandler = urllib2.HTTPBasicAuthHandler(passman)    
        opener = urllib2.build_opener(authhandler)    
        urllib2.install_opener(opener)
        
        pagehandle = urllib2.urlopen('https://tcms.engineering.redhat.com/case/' + caseid + '/?from_plan=' + planid)
#        data = pagehandle.read().decode('utf-8')
        data = pagehandle.read()
        pagehandle.close()
        return data

    def lastchange(self, data):
        lstchange_cmp = re.compile('\t{4}<td>\n\
(\s*\n)+\
\t{6}(.*)<br/>\n\
(\s*\n)+\
\t{4}</td>\n\
\t{4}<td>')

        changesearch = re.findall(lstchange_cmp, data)
        resultlen = len(changesearch)
        if resultlen:
            return changesearch[resultlen - 1][1]
        else:
            return 'nobody'

    def changelogmark(self):
        fh_read = open(self.filein)
        fh_final = open(self.filein + '.final', 'w')
        caseidlist = self._caseid_list(self.filein)
        cntnm = 1
        for caseid in caseidlist:
            print cntnm, caseid, 'S' * 90
            data = self._case_html_read(caseid, self.planid)
            lastman = self.lastchange(data)
            print lastman
            fh_final.write(fh_read.readline().rstrip() + '\t' + lastman + os.linesep)
            fh_final.flush()
            cntnm += 1
        fh_read.close()
        fh_final.close()

ggg = ChangeLogMark('0131_6578.sort_needupdate', 6578)
ggg.changelogmark()
#data = ggg._case_html_read(177633, 6578)
#ggg.lastchange(data)

#ggg.lastchange(open('data').read())





