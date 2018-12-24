import itertools
from operator import itemgetter

import ujson

from Parse import Parse
from Ranker import Ranker


class Searcher:
    def __init__(self, stopWords, postPath, doStem, baseDict, fileIndex, showEntities, doSemantics, citiesList=None):
        self.baseDic = baseDict
        self.fileIndex = fileIndex
        self.stopWords = stopWords
        self.citiesList = citiesList
        self.ranker = Ranker(self.baseDic, self.fileIndex, postPath, doStem)
        self.stopWords = stopWords
        self.citiesList = citiesList
        self.showEntities = showEntities
        self.doSemantics = doSemantics
        with open("simDict.ujson", "r+") as Jfile:
            self.similarityDict = ujson.load(Jfile)
        Jfile.close()

    def singleQueryCalc(self, query):
        parseQuery = Parse(self.stopWords).parseText(query)
        self.ranker.query = parseQuery
        if(self.doSemantics == 1):
            semanticQuery = []
            for w in parseQuery:
                semanticQuery.append(w)
                if(w in self.similarityDict):
                    for sim in self.similarityDict[w.lower()]:
                        semanticQuery.append(sim[0])
            #print(semanticQuery)
            resList = self.ranker.calculateRate(semanticQuery)
        else:
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
        # print(theRanking)
        if (self.showEntities == 1):
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
            if (self.doSemantics == 1):
                semanticQuery = []
                for w in parseQuery:
                    semanticQuery.append(w)
                    for sim in self.similarityDict[w]:
                        semanticQuery.append(sim[0])
                print(semanticQuery)
                resList = self.ranker.calculateRate(semanticQuery)
            else:
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
            if (self.showEntities == 1):
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
            # print(entitiesDict)
            for word in entitiesDict:
                if (word in self.baseDic):
                    ansDict[word] = entitiesDict[word]
            # print("ANS: ", ansDict)
            # x = itertools.islice(ansDict.items(), 0, 5)
            # i = sorted(ansDict.values(),reverse=True)[0]

            x = sorted(ansDict.items(), key=itemgetter(1), reverse=True)
            i = self.fileIndex[tuple[0]][4]
            for e in x:
                entitiesToShow.append((e[0], e[1] / i))
            # print(entitiesToShow)
            result[tuple] = entitiesToShow
        return result
        # print("FINAL: ", result)
