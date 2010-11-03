

__author__="Andre Rattinger"
__date__ ="$09.09.2010 10:52:25$"


STREAMSOURCE = ["PROCESSBATCH",         #0
                "PROCESSCONTINUOUS",    #1
                "EQUIPMENT",            #2
                "WHEE",                 #3
                "DISTRIBUTIONLINE",     #4
                "HXPROPOSAL"]           #5

STREAMTYPE = ["STARTUP",                #0
              "CIRCULATION",            #1
              "MAINTAINANCE",           #2
              "WASTEHEATABOVECOND",     #3
              "WASTEHEATCOND",          #4
              "WASTEHEATBELOWCOND",     #5
              "EXHAUSTGAS",             #6
              "EXHAUSTGASCOND",         #7
              "COMBUSTIONAIR",          #8
              "BOILERFEEDWATER",        #9
              "CONDENSATERECOVERY",     #10
              "SENSIBLEHEAT",           #11
              "WASTEHEAT",              #12
              "HXPROPOSAL"]             #13
              
if __name__ == "__main__":
    print "Hello World";
