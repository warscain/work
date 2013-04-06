#!/usr/bin/env python
# -*- coding: utf-8 *-*

import os
import re
import urllib
import urllib2
import cookielib

class CaseSortList(object):
    def __init__(self, filein, fileout):
        self.case_sort(self.case_all(filein), fileout)

    def _st_key(self, line):
        '''return a tuple (feature name, case id)'''
        line_cmp = re.compile('\
^(\d{6})\
\s+\
(\
(\[[^\[,\]]*\])|(\w+)|(.))\
\s*\
.*')
        line_search = re.search(line_cmp, line)
        return line_search.group(2).lower(), line_search.group(1)

    def case_all(self, filein):
        fh_in = open(filein, 'r')
#        fh_out = open(filein+'tmp', 'w')
        # cut the blank and not useful strings, return the new list
        case_list = []
        linecmp = re.compile('\
(^\s+)\
(\d{6}\s+.*[^\s])\
(\s+[a-z]+)\
(\s+[a-z,N]+)\
((\s+[a-z,M,A,B]+)|(\s+[a-z,M]+)(\s+\([a-z,A]+\)))\
((\s+[\w-]+)|(\s+\w+)(\s+\w+))\
(\s+P\d)\
(\s+(None|\d+))\
(\s+Edit)\
')
        for line in fh_in:
            line_result = re.search(linecmp, line).group(2) + os.linesep
#            fh_out.write(line_result)
            case_list.append(line_result)
        fh_in.close()
#        fh_out.close()
        return case_list

    def case_sort(self, case_list, fileout):
        case_list.sort(key=self._st_key)

        fh_out = open(fileout, 'w')
        for finalline in case_list:
            fh_out.write(finalline)
        fh_out.close()

#newcasefile = CaseList('6578sweep', '6578sweep.1')

class BZJudge(object):
    def __init__(self):
        self._get_cookie()
    
    def _get_cookie(self):
        url = 'https://bugzilla.redhat.com/index.cgi?GoAheadAndLogIn=1'
        values = {"Bugzilla_login": "xxxxxxx@xxxxx.com",
                  "Bugzilla_password": "xxxxxxxx",
                  "GoAheadAndLogin": "Log in"}

        request= urllib2.Request(url, urllib.urlencode(values))
        request.add_header('User-Agent', 'Mozilla/5.0')
        ckjar = cookielib.MozillaCookieJar('cookie.cie')
        ckproc = urllib2.HTTPCookieProcessor(ckjar)
        opener = urllib2.build_opener(ckproc)
        f = opener.open(request)
#        htm = f.read()
        f.close()
        ckjar.save(ignore_discard=True, ignore_expires=True)
    
    def bz_status(self, bugid):
            bugid = str(bugid)
            url_get = 'https://bugzilla.redhat.com/show_bug.cgi?id=' + bugid
            filename = 'cookie.cie'
            ckjar = cookielib.MozillaCookieJar()
            ckjar.load(filename)
            ckproc = urllib2.HTTPCookieProcessor(ckjar)
            opener = urllib2.build_opener(ckproc)
            request = urllib2.Request(url_get)
            request.add_header('User-Agent', 'Mozilla/5.0')
            content = opener.open(request)
        
            for line in content:
                if line.startswith('      <span id="static_bug_status">'):
                    bug_status = line.split('>')[1].rstrip()
#                    if bug_status in ['NEW', 'ASSIGNED', 'RELEASE_PENDING', 'ON_DEV', 'POST']: # BUG没修好的
                    if bug_status in ['NEW', 'ASSIGNED', 'MODIFIED', 'ON_QA', 'RELEASE_PENDING', 'ON_DEV', 'POST']: # BUG没修好的
                        print bugid, bug_status
                        return True
                    else:
                        print bugid, bug_status
                        return False

    def bz_list_result(self, buglist):
        result = 0
        bz_result_dict = {}
        for bugid in buglist:
            if self.bz_status(bugid):
                result = 1
                bz_result_dict[bugid] = 1
            else:
                bz_result_dict[bugid] = 0
        print bz_result_dict
        return result

class CaseBZJudge(object):
    def __init__(self, filein):
        self.finein = filein
        self.bz = BZJudge()
        self.judge(self.finein)
    def judge(self, filein):
        filein_hd = open(filein, 'r')
        bugid_cmp = re.compile('.([0-9]{6})')

        file_needupdate = open(filein+'_needupdate', 'w')
        file_notneedupdate = open(filein+'_notneedupdate', 'w')

        for line in filein_hd:
            result_bugid = re.findall(bugid_cmp, line)

            if result_bugid:
                print 'S' * 50
                print 'result_buglist:', result_bugid
                if self.bz.bz_list_result(result_bugid):
                    print 'Bug not fixed, Case not need update'
                    file_notneedupdate.write(line)
                    file_notneedupdate.flush()
                else:
                    print 'Bug fixed, Case need update'
                    file_needupdate.write(line)
                    file_needupdate.flush()
                print 'E' * 50
            else:
                print 'S' * 50
                print 'result_buglist:', result_bugid
                print 'case subject not include bugid and case is needupdate, Case may need update'
                file_needupdate.write(line)
                file_needupdate.flush()
                print 'E' * 50


class BlackListMark(object):
    def __init__(self, filein, caseidlist):
        self.blacklist_file_change(filein, caseidlist)

    def _file_change(self, filein, caseid, flag):
        caseid = str(caseid)
        fh = open(filein, 'r+')
        lastell = 0
        curtell = 0
        while True:
            line = fh.readline()
            lastell, curtell = curtell, fh.tell()
            if line:
                if re.search('^' + caseid, line):
                    fh.seek(lastell)
                    fh.write(re.sub('^' + caseid + '\t', caseid + flag, line))
                    break
            else:
                break
        fh.flush()
        fh.close()

    def blacklist_file_change(self, filein, caseidlist):
        for FB_caseid in caseidlist[0]:
            self._file_change(filein, FB_caseid, 'P')
        for TB_caseid in caseidlist[1]:
            self._file_change(filein, TB_caseid, 'T')


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
        passman.add_password(None, url, 'xxxxxx', 'xxxxxxxx')
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
            print cntnm, caseid, 'S' * 50
            data = self._case_html_read(caseid, self.planid)
            lastman = self.lastchange(data)
            print lastman
            fh_final.write(fh_read.readline().rstrip() + '\t' + lastman + os.linesep)
            fh_final.flush()
            print 'E' * 50
            cntnm += 1
        fh_read.close()
        fh_final.close()



casefile = '0304_6578'
casesortfile = casefile + '.' + 'sort'
caseupdatefile = casesortfile + '_needupdate'
planid = 6578

#blacklist case numbers
permanent_blacklist = [
                       176512,
                       176514,
                       176511
               ]

temporary_blacklist = [
                       226913,
               ]

blackcaselist = [permanent_blacklist, temporary_blacklist]

if __name__ == '__main__':
    casesort = CaseSortList(casefile, casesortfile) # <-- casefile | --> casesortfile

    casejudge = CaseBZJudge(casesortfile) # <-- casesortfile | --> caseupdatefile

    caseblacklist = BlackListMark(caseupdatefile, blackcaselist) # <-- caseupdatefile | --> caseupdatefile

    lastman = ChangeLogMark(caseupdatefile, planid) # <-- caseupdatefile | --> caseupdatefile.final
    lastman.changelogmark()