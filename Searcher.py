import itertools

import ujson

from Parse import Parse
from Ranker import Ranker


class Searcher:
    def __init__(self, stopWords, postPath, doStem, citiesList=None):
        if (doStem):
            with open(postPath + "/S_baseDict.ujson", "r+") as file:
                self.baseDic = ujson.load(file)
                file.close()
            with open(postPath + "/S_fileIndex.ujson", "r+") as file1:
                self.fileIndex = ujson.load(file1)
                file1.close()
        else:
            with open(postPath + "/baseDict.ujson", "r+") as file:
                self.baseDic = ujson.load(file)
                file.close()
            with open(postPath + "/fileIndex.ujson", "r+") as file1:
                self.fileIndex = ujson.load(file1)
                file1.close()
        self.ranker = Ranker(self.baseDic, self.fileIndex, postPath, doStem)
        self.stopWords = stopWords
        self.citiesList = citiesList

    def singleQueryCalc(self, query):
        parseQuery = Parse(self.stopWords).parseText(query)
        # self.ranker.query = parseQuery
        resList = self.ranker.calculateRate(parseQuery)
        theRanking = []
        if (self.citiesList != None):
            for city in self.citiesList:
                for doc in resList:
                    if (self.fileIndex[doc][2] == city):
                        theRanking.append((doc,resList[doc]))
        else:
            x = itertools.islice(resList.items(), 0, 50)
            for i in x:
                theRanking.append(i)
        print (theRanking)

    def multiQueryCalc(self, queryFile):
        querysDict = {}
        resultDict = {}
        with open(queryFile + ".txt", "r+") as querysFile:
            inPart = False
            queryText = ""
            queryNum = ""

            for line in querysFile:
                if (inPart):
                    querysDict[queryNum] = queryText
                    inPart = False
                if ("<num>" in line):
                    queryNum = line[line.index('>') + 1:].split(": ")[1].strip()
                elif ("<title>" in line):
                    queryText = (line[line.index('>') + 1:].strip())
                    inPart = True
            querysFile.close()
        for q in querysDict:
            parseQuery = Parse(self.stopWords).parseText(querysDict[q])
            resList = self.ranker.calculateRate(parseQuery)
            theRanking = []
            if (self.citiesList != None):
                for city in self.citiesList:
                    for doc in resList:
                        if (self.fileIndex[2] == city):
                            theRanking.append(doc)
            else:
                x = itertools.islice(resList.items(), 0, 50)
                for doc in x:
                    theRanking.append(doc)
            resultDict[q] = theRanking
        print(resultDict)
