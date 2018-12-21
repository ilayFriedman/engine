import itertools
from operator import itemgetter

import ujson

from Parse import Parse
from Ranker import Ranker


class Searcher:
    def __init__(self, stopWords, postPath, doStem, showEntities, citiesList=None):
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
        self.showEntities = showEntities

    def singleQueryCalc(self, query):
        parseQuery = Parse(self.stopWords).parseText(query)
        # self.ranker.query = parseQuery
        resList = self.ranker.calculateRate(parseQuery)
        tmpDict = {}
        theRanking = []
        if (self.citiesList != None):
            for city in self.citiesList:
                for doc in resList:
                    if (self.fileIndex[doc][2] == city):
                        tmpDict[doc] = resList[doc]
                x = itertools.islice(tmpDict.items(), 0, 50)
                theRanking.clear()
                for i in x:
                    theRanking.append(i)
        else:
            x = itertools.islice(resList.items(), 0, 50)
            for i in x:
                theRanking.append(i)
        #print(theRanking)
        if (self.showEntities):
            print(self.addEntities(theRanking))
            return self.addEntities(theRanking)
        else:
            print(theRanking)
            return theRanking

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
            tmpDict = {}
            theRanking = []
            if (self.citiesList != None):
                for city in self.citiesList:
                    for doc in resList:
                        if (self.fileIndex[doc][2] == city):
                            tmpDict[doc] = resList[doc]
                    x = itertools.islice(tmpDict.items(), 0, 50)
                    theRanking.clear()
                    for i in x:
                        theRanking.append(i)
            else:
                x = itertools.islice(resList.items(), 0, 50)
                for doc in x:
                    theRanking.append(doc)
            if (self.showEntities):
                resultDict[q] = self.addEntities(theRanking)
            else:
                resultDict[q] = theRanking
        print(resultDict)

    def addEntities(self, docList):
        entitiesDict = {}

        result = {}
        for tuple in docList:
            entitiesToShow = []
            ansDict = {}
            entitiesDict = self.fileIndex[tuple[0]][5]
            #print(entitiesDict)
            for word in entitiesDict:
                if (word in self.baseDic):
                    ansDict[word] = entitiesDict[word]
            #print("ANS: ", ansDict)
            #x = itertools.islice(ansDict.items(), 0, 5)
            #i = sorted(ansDict.values(),reverse=True)[0]

            x = sorted(ansDict.items(), key=itemgetter(1), reverse=True)
            i = self.fileIndex[tuple[0]][4]
            for e in x:
                entitiesToShow.append((e[0], e[1]/i))
            #print(entitiesToShow)
            result[tuple] = entitiesToShow
        return result
            #print("FINAL: ", result)
