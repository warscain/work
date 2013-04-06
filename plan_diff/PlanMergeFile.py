#!/usr/bin/env python
# -*- coding: utf-8 *-*

import re

class PlanDiff(object):
    def __init__(self, file_in_old, file_in_new):
        pass
        self.oldplan_all = self.old_plan(file_in_old)
        self.newplan_all = self.new_plan(file_in_new)

    def _case_section(self, filehd):
        casenamecmp = re.compile('\
(^\s+)\
(\d{6}\s+(.*[^\s]))\
(\s+[a-z]+)\
(\s+[a-z,N]+)\
((\s+[a-z,M,A,B]+)|(\s+[a-z,M]+)(\s+\([a-z,A]+\)))\
((\s+[\w-]+)|(\s+\w+)(\s+\w+))\
(\s+P\d)\
(\s+(None|\d+))\
(\s+Edit)\
')
        CaseDict = {}
        for line_old in filehd:
            casename_search = re.search(casenamecmp, line_old)
            if casename_search:
                casename = casename_search.group(3)
                CaseDict[casename] = ''
            else:
                CaseDict[casename] += line_old
        return CaseDict
            
    def old_plan(self, file_in_old):
        return self._case_section(open(file_in_old))

    def new_plan(self, file_in_new):
        return  self._case_section(open(file_in_new))


if __name__ == '__main__':
    diff = PlanDiff('6578tmp', '6578all')
    for itemold in diff.oldplan_all:
        if itemold in diff.newplan_all:
            if diff.oldplan_all[itemold] == diff.newplan_all[itemold]:
                pass
            else:
                print 'CaseBody Not Same:', itemold
        else:
            print 'Case Not In New Plan:',itemold



