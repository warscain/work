#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import re
import os

class PlanMerge(object):

    def __init__(self):
        pass

    def _caseid_list(self, filein):
        fh_filein = open(filein)
        linecmp = re.compile('\
(^\s+)\
((\d{6})\s+.*[^\s])\
(\s+[a-z]+)\
(\s+[a-z,N]+)\
((\s+[a-z,M,A,B]+)|(\s+[a-z,M]+)(\s+\([a-z,A]+\)))\
((\s+[\w-]+)|(\s+\w+)(\s+\w+))\
(\s+P\d)\
(\s+(None|\d+))\
(\s+Edit)\
')
        caseidlist = []
        for line in fh_filein:
            caseid_search = re.search(linecmp, line)
            if caseid_search:
                caseidlist.append(caseid_search.group(3))
        print 'All cases num:', len(caseidlist)
        return caseidlist

    def case_html_read(self, caseid, planid):
        caseid = str(caseid)
        planid = str(planid)
        #fileout = open('fileout', 'w')
        url = 'https://tcms.engineering.redhat.com/case/' + caseid + '/?from_plan=' + planid
        # this creates a password manager
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, url, 'xxxxxx', 'xxxxxxx')
        # create the AuthHandler
        authhandler = urllib2.HTTPBasicAuthHandler(passman)    
        opener = urllib2.build_opener(authhandler)    
        urllib2.install_opener(opener)
        
        pagehandle = urllib2.urlopen('https://tcms.engineering.redhat.com/case/' + caseid + '/?from_plan=' + planid)
#        data = pagehandle.read().decode('utf-8')
        data = pagehandle.read()
        pagehandle.close()
        return data

    def case_detail(self, data):
        case_detail = ['', {#'Status': None,
                         'Notes': None, 
                         'Setup': None, 
                         'Breakdown': None, 
                         'Actions': None, 
                         'Expected Results': None}]
        c_name_cmp = re.compile('<title>Test\s+case\s+-\s+[0-9]{6}:\s(.*)</title>')
        
#        c_status_cmp = re.compile('\s+<div class="title grey">Status&nbsp;:</div>\n\
#\s+<div class="name"><span id="display_priority" >(.*)</span></div>\n\
#\s+</div>')

        c_notes_cmp = re.compile('<div class="title grey">Notes&nbsp;:</div>\n\
\s+<div class="name" style="max-width:800px;"><span id="display_priority" >([\s\S]*)</span></div>\n\
\s+</div>\n\
\s+</fieldset>\n\
\s+</div>\n\
\s+\n\
\s+<div class="Detailform border-1">')
        c_setup_cmp = re.compile('\s+<td valign="top" >\n\
\s+<h4>Setup:</h4>\n\
\s+<div class="casedoc">([\s\S]*)</div>\n\
\s+</td>\n\
\s+<td valign="top" >\n\
\s+<h4>Breakdown:</h4>')
        c_breakdown_cmp = re.compile('\s+<td valign="top" >\n\
\s+<h4>Breakdown:</h4>\n\
\s+<div class="casedoc">([\s\S]*)</div>\n\
\s+</td>\n\
\s+</tr>\n\
\s+<tr>\n\
\s+<td valign="top">\n\
\s+<h4>Actions:</h4>')
        c_actions_cmp = re.compile('\s+<td valign="top">\n\
\s+<h4>Actions:</h4>\n\
\s+<div class="casedoc">([\s\S]*)</div>\n\
\s+</td>\n\
\s+<td valign="top" >\n\
\s+<h4>Expected Results:</h4>')
        c_expect_result_cmp = re.compile('\s+<td valign="top" >\n\
\s+<h4>Expected Results:</h4>\n\
\s+<div class="casedoc">([\s\S]*)</div>\n\
\s+</td>\n\
\s+</tr>\n\
</table>')
        case_detail[0] = re.search(c_name_cmp, data).group(1)
#        case_detail[1]['Status'] = re.search(c_status_cmp, data).group(1)
        case_detail[1]['Notes'] = re.search(c_notes_cmp, data).group(1)
        case_detail[1]['Setup'] = re.search(c_setup_cmp, data).group(1)
        case_detail[1]['Breakdown'] = re.search(c_breakdown_cmp, data).group(1)
        case_detail[1]['Actions'] = re.search(c_actions_cmp, data).group(1)
        case_detail[1]['Expected Results'] = re.search(c_expect_result_cmp, data).group(1)
        return case_detail

    def allcase_big_list(self, caseidlist, planid):
        CaseBigList = []
        caseidcount = 1
        for caseid in caseidlist:
            print '=' * 50 ###
            print 'Case id:', caseid, 'Case read in count:', caseidcount, 'Plan id:', planid ###
            data = self.case_html_read(caseid, planid)
            case_detail = self.case_detail(data)
            print case_detail ###
            CaseBigList.append(case_detail)
            caseidcount += 1
            print 'Cases in Big List:', len(CaseBigList) ###
            print '=' * 50 ###
        print 'Cases in Big List Final:', len(CaseBigList)
        return CaseBigList

    def oldplan_needmerge(self, planfile_old_in, planid_old, planfile_new_in, planid_new):
        CaseBigList_old = self.allcase_big_list(self._caseid_list(planfile_old_in), planid_old)
        CaseBigList_new = self.allcase_big_list(self._caseid_list(planfile_new_in), planid_new)

        fh_needcreate = open('resultneedcreate', 'w')
        fh_needupdate = open('resultneedupdate', 'w')
        fh_caseall = open('resultall', 'w')

        CBL_new_itemlist = [ item[0] for item in CaseBigList_new]
        for itemold in CaseBigList_old:
            if itemold in CaseBigList_new:
#                print 'Case Same:', itemold
                fh_caseall.write('Case Same:' + '\t' + itemold[0] + os.linesep)
            else:
                if itemold[0] in CBL_new_itemlist:
#                    print 'Case Need Update:', itemold
                    fh_needupdate.write(itemold[0] + os.linesep)
                    fh_caseall.write('Case Need Update:' + '\t' + itemold[0] + os.linesep)
                else:
#                    print 'Case Need Create:', itemold
                    fh_needcreate.write(itemold[0] + os.linesep)
                    fh_caseall.write('Case Need Create:' + '\t' + itemold[0] + os.linesep)
#            fh_needcreate.flush()
#            fh_needupdate.flush()
#            fh_caseall.flush()
        fh_needcreate.close()
        fh_needupdate.close()
        fh_caseall.close()


vvv = PlanMerge()
#caselist = vvv._caseid_list('6578sweep')
#print vvv.allcase_big_list([176692], 6578)
vvv.oldplan_needmerge('6578allshort', 6578, '7651allshort', 7651)
#vvv.oldplan_needmerge('6578all', 6578, '7651all', 7651)







