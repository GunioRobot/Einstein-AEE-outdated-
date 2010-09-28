# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Andre Rattinger"
__date__ ="$09.09.2010 10:52:25$"


STREAMSOURCE = ["PROCESSBATCH",
                "PROCESSCONTINUOUS",
                "EQUIPMENT",
                "WHEE",
                "DISTRIBUTIONLINE"]

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
              "WASTEHEAT"]              #12

              
if __name__ == "__main__":
    print "Hello World";
