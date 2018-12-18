import itertools

import ujson

from Parse import Parse
from Ranker import Ranker


class Searcher:
    def __init__(self, stopWords, postPath, doStem):
        if (doStem):
            with open(postPath + "/S_baseDict.ujson", "r+") as file:
                baseDic = ujson.load(file)
                file.close()
            with open(postPath + "/S_fileIndex.ujson", "r+") as file1:
                fileIndex = ujson.load(file1)
                file1.close()
        else:
            with open(postPath + "/baseDict.ujson", "r+") as file:
                baseDic = ujson.load(file)
                file.close()
            with open(postPath + "/fileIndex.ujson", "r+") as file1:
                fileIndex = ujson.load(file1)
                file1.close()
        self.ranker = Ranker(baseDic, fileIndex, postPath, doStem)
        self.stopWords = stopWords

    def singleQueryCalc(self, query):
        parseQuery = Parse(self.stopWords).parseText(query)
        #self.ranker.query = parseQuery
        resList = self.ranker.calculateRate(parseQuery)
        x = itertools.islice(resList.items(), 0, 50)
        theRanking = []
        for i in x:
            theRanking.append(i)
        return (theRanking)

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
            x = itertools.islice(resList.items(), 0, 50)
            theRanking = []
            for i in x:
                theRanking.append(i)
            resultDict[q] = theRanking
        print(resultDict)

