import itertools
import timeit
from collections import defaultdict
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
        self.citiesList = citiesList
        self.showEntities = showEntities
        self.doSemantics = doSemantics
        with open("simDictM.ujson", "r+") as Jfile:
            self.similarityDict = ujson.load(Jfile)
        Jfile.close()

    def singleQueryCalc(self, query):
        #print("LEN SIM: ", len(self.similarityDict))
        parseQuery = Parse(self.stopWords).parseText(query)
        self.ranker.query = parseQuery
        if(self.doSemantics == 1):
            semanticQuery = []
            for w in parseQuery:
                semanticQuery.append(w)
                if(w.lower() in self.similarityDict):
                    for sim in self.similarityDict[w.lower()]:
                        if(sim[0] not in semanticQuery):
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
                x = itertools.islice(tmpDict.items(), 0, 1200)
                theRanking.clear()
                for i in x:
                    theRanking.append(i)
        else:
            x = itertools.islice(resList.items(), 0, 1200)
            for i in x:
                theRanking.append(i)
        # print(theRanking)
        if (self.showEntities == 1):
            #print(self.addEntities(theRanking))
            return self.addEntities(theRanking)
        else:
            #print(theRanking)
            return theRanking

    def multiQueryCalc(self, queryFile):
        start = timeit.default_timer()
        querysDict = defaultdict(list)
        resultDict = {}
        with open(queryFile, "r+") as querysFile:
            inPart = False
            startDescReading=False
            queryText = ""
            queryNum = ""
            descText=""

            for line in querysFile:
                if (inPart):
                    querysDict[queryNum][0] = queryText
                    querysDict[queryNum][1] = descText
                    del descText
                    inPart = False
                if ("<num>" in line):
                    queryNum = line[line.index('>') + 1:].split(": ")[1].strip()
                elif ("<title>" in line):
                    queryText = (line[line.index('>') + 1:].strip())
                elif("<narr>" in line):
                    startDescReading=False
                    inPart = True
                elif(startDescReading):
                    descText += line.strip()+" "
                elif ("<desc>" in line):
                    startDescReading=True

            querysFile.close()
        destStopWords =["etc.", "i.e", "considered", "information", "documents", "document", "discussing", "discuss", "following",
         "issues", "identify", "find", "must"]
        for q in querysDict:
            parseQuery = Parse(self.stopWords).parseText(querysDict[q][0])
            parseQuery += Parse(list(set().union(self.stopWords,destStopWords))).parseText(querysDict[q][1])
            if (self.doSemantics == 1):
                #semanticQuery = []
                for w in parseQuery:
                    #semanticQuery.append(w)
                    if (w.lower() in self.similarityDict):
                        for sim in self.similarityDict[w.lower()]:
                            if (sim[0] not in querysDict[q][2]):
                                #semanticQuery.append(sim[0])


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
                for doc in x:
                    theRanking.append(doc)
            if (self.showEntities == 1):
                resultDict[(q,querysDict[q][0])] = self.addEntities(theRanking)
            else:
                resultDict[(q,querysDict[q][0])] = theRanking
        self.createAnswerFile(resultDict)
        #print(resultDict)
        stop = timeit.default_timer()
        print("### Time to Answer ###", stop - start, "seconds")
        return(resultDict)

    def createAnswerFile(self, results):
        with open("trec/ourAnswers.txt","w+") as file:
            for res in results.keys():
                for i in results[res]:
                    string = str(res[0]) + " 0 " + i[0] + " 1"
                    file.write(string + "\n")
            file.close()

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
            x = sorted(ansDict.items(), key=itemgetter(1), reverse=True)
            x = itertools.islice(x, 0, 5)
            i = self.fileIndex[tuple[0]][4]
            for e in x:
                entitiesToShow.append((e[0], e[1] / i))
            #print(entitiesToShow)
            result[tuple] = entitiesToShow
        return result
        # print("FINAL: ", result)
