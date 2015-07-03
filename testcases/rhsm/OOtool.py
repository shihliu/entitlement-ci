##############################################################################
## File Description
##############################################################################
"""
OOtool stands for OBJECT ORGANIZER TOOL
These scripts are meant to be used in the python interpretor when looking for object types (eg. buttons, tables, labels, etc.)
This script links up with the dictionary with the guilocator file to sort out the buttons and tables, etc. that have already been linked up with
a name.

To use simply be in the current directory and type import OOtool in the python interpretor.
Or, you can use

from OOtool import *

if you are really lazy.

Sample output:


OOtool.getMatchedBtnList('register-dialog')



******************************************************
The following BUTTONS have been matched


******************************************************

dialog-register-button                    -------------------maps to------------------->        btnregisterbutton
dialog-cancle-button                      -------------------maps to------------------->        btncancelbutton
configure-proxy-button                    -------------------maps to------------------->        btnproxybutton



******************************************************
The following BUTTONS have NOT been matched


******************************************************

btnWhyShouldIRegister?
btndefaultbutton



******************************************************
"""
##############################################################################
import rhsmguilocator
import ldtp

GUI_DICT = rhsmguilocator.RHSMGuiLocator().element_locators
DOT_LINE = "******************************************************"
ARROW = " -------------------maps to------------------->        "
START_DOT_LINE = "\n\n\n" + DOT_LINE + "\n"
END_DOT_LINE = "\n" + DOT_LINE + "\n\n\n"

print START_DOT_LINE
print 'Type "functions()" or OOtool.functions() (depends on how you imported this module) to get info on functions this module provides'
print END_DOT_LINE

################################
## Helper Functions
################################

def printSection(sectionTitle):
    print START_DOT_LINE + sectionTitle + START_DOT_LINE

def mapFromList(toFind, L):
    for key in GUI_DICT:
        if GUI_DICT[key] == toFind:
            spacedKey = key
            while len(spacedKey) <= 40: 
                spacedKey += " "
            print spacedKey + ARROW + toFind
            return True
    return False

def sortObjectList(L, *keywords):
    sortedList = []
    for item in L:
        for keyword in keywords:
            if item.startswith(keyword):
                sortedList += [item]
    return sortedList

def printFoundReturnUnfound(objectList):
    unfound = []
    for objectOne in objectList:
        if not(mapFromList(objectOne, objectList)):
            unfound += [objectOne]
    return unfound

def printUnfounds(unfoundWindowList):
    for unfoundWindow in unfoundWindowList:
        print unfoundWindow
    print START_DOT_LINE

def getMatchedVariableList(variableType, variableList):
    variableType = variableType.upper()
    printSection("The following " + variableType + " have been matched")
    unfoundList = printFoundReturnUnfound(variableList)
    printSection("The following " + variableType + " have NOT been matched")
    for unfound in unfoundList:
        print unfound
    print START_DOT_LINE

def getTypeList(windowName, *objectTypes):
    if windowName in GUI_DICT:
        windowName = GUI_DICT[windowName]
    return sortObjectList(ldtp.getobjectlist(windowName), objectTypes)

def printFunctDesc(objectTypeShortName, objectType):
    print ("getMatched%sList(WINDOW) --- gets detailed info (including matched and unmatched) on all %s in the window WINDOW." % (objectTypeShortName, objectType))


################################
## Core User Functions
################################

def functions():
    print "Functions provided:"
    print "NOTE: All WINDOW arguements in the following function can be can be in ldtp form \n     (eg. 'frmSubscriptionManager')or labeled form (eg. 'main-window')\n"
    print "getMatchedWindowList() --- gets the window list and lists out which windows are matched and which ones are not."
    printFunctDesc("Btn", "buttons")
    printFunctDesc("Tbl", "tabels")
    printFunctDesc("Tbtn", "toggle-buttons")
    printFunctDesc("Lbl", "labels")
    printFunctDesc("Ptab", "page-tabs")
    printFunctDesc("Lbl", "labels")
    printFunctDesc("Txt", "texts (text-boxes)")
    printFunctDesc("Ptab", "page-tabs")
    printFunctDesc("Tch", "table-column-headers")
    printFunctDesc("Trh", "table-row-headers")
    print "getMatchedKeywordList(WINDOW, KEYWORD) --- gets all objects (with detailed info) in window WINDOW that have the keyword KEYWORD in it."


def getMatchedWindowList():
    windowList = ldtp.getwindowlist()
    getMatchedVariableList("windows", windowList)

def getMatchedBtnList(windowName):
    getMatchedVariableList("buttons", getTypeList(windowName, "btn"))

def getMatchedTblList(windowName):
    getMatchedVariableList("tabels", getTypeList(windowName, "tbl", "ttbl"))

def getMatchedTbtnList(windowName):
    getMatchedVariableList("toggle-buttons", getTypeList(windowName,"tbtn"))

def getMatchedLblList(windowName):
    getMatchedVariableList("labels", getTypeList(windowName,"lbl"))

def getMatchedTxtList(windowName):
    getMatchedVariableList("texts", getTypeList(windowName,"txt"))

def getMatchedPtabList(windowName):
    getMatchedVariableList("page-tabs", getTypeList(windowName,"ptab"))

def getMatchedTchList(windowName):
    getMatchedVariableList("table-column-headers", getTypeList(windowName,"tch"))

def getMatchedTrhList(windowName):
    getMatchedVariableList("table-row-headers", getTypeList(windowName,"trh"))

def getMatchedKeywordList(windowName, keyword):
    if windowName in GUI_DICT:
        windowName = GUI_DICT[windowName]
    sortedList = []
    for item in ldtp.getobjectlist(windowName):
        if keyword.lower() in item.lower():
            sortedList += [item]
    printSection('The following objects with keyword "%s" have been matched' % keyword)
    unfounds = printFoundReturnUnfound(sortedList)
    printSection('The following objects with keyword "%s" have NOT been matched' % keyword)
    printUnfounds(unfounds)

def printDict():
    print GUI_DICT

