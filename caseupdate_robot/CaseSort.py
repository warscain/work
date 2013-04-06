import re

class CaseList(object):
    def __init__(self, filein, fileout):
        self.case_sort(self.case_all(filein), fileout)

    def _st_key(self, line):
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
            line_result = re.search(linecmp, line).group(2) + "\n"
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

case6578 = CaseList('caseall6578', 'caseall6578.sort')