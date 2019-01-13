import itertools
import re
import timeit
from collections import defaultdict
from operator import itemgetter

import ujson

from nltk import PorterStemmer

from Parse import Parse
from Ranker import Ranker


class Searcher:
    def __init__(self, stopWords, postPath, doStem, baseDict, fileIndex, showEntities, doSemantics, citiesList=None):
        self.baseDic = baseDict
        self.fileIndex = fileIndex
        with open(stopWords, "r+") as SW:
            self.stop_words = map(str.strip, SW.readlines())
        SW.close()
        self.stop_words = set(self.stop_words)
        self.citiesList = citiesList
        self.doStem = doStem
        self.ranker = Ranker(self.baseDic, self.fileIndex, postPath, doStem)
        self.citiesList = citiesList
        self.showEntities = showEntities
        self.doSemantics = doSemantics
        with open("simDictXL.ujson", "r+") as Jfile:
            self.similarityDict = ujson.load(Jfile)
        Jfile.close()

    def singleQueryCalc(self, query):
        # print("LEN SIM: ", len(self.similarityDict))
        parseQuery = Parse(self.stop_words).parseText(query)
        if(self.doStem == 1):
            parseQuery = self.makeStemList(parseQuery)
        self.ranker.query = parseQuery
        if (self.doSemantics == 1):
            semanticQuery = []
            for w in parseQuery:
                semanticQuery.append(w)
                if (w.lower() in self.similarityDict):
                    for sim in self.similarityDict[w.lower()]:
                        if (sim[0] not in semanticQuery):
                            semanticQuery.append(sim[0])
            # print(semanticQuery)
            resList = self.ranker.calculateRate(semanticQuery, False)
        else:
            resList = self.ranker.calculateRate(parseQuery, False)

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
            # print(self.addEntities(theRanking))
            return self.addEntities(theRanking)
        else:
            # print(theRanking)
            return theRanking

    def multiQueryCalc(self, queryFile):
        start = timeit.default_timer()
        querysDict = defaultdict(list)
        resultDict = {}
        nerrative = self.nerrativeMaker(queryFile)
        with open(queryFile, "r+") as querysFile:
            inPart = False
            startDescReading = False
            queryText = ""
            queryNum = ""
            descText = ""
            #+ str(nerrative[queryNum][1])
            stop = timeit.default_timer()
            for line in querysFile:
                if (inPart):
                    querysDict[queryNum] = [queryText, descText+ str(nerrative[queryNum][1]), [],[]]
                    del descText
                    descText = ""
                    inPart = False
                if ("<num>" in line):
                    queryNum = line[line.index('>') + 1:].split(": ")[1].strip()
                elif ("<title>" in line):
                    queryText = (line[line.index('>') + 1:].strip()).lower()
                elif ("<narr>" in line):
                    startDescReading = False
                    inPart = True
                elif (startDescReading):
                    descText += line.lower().strip() + " "
                elif ("<desc>" in line):
                    startDescReading = True

            querysFile.close()
            stop = timeit.default_timer()
        destStopWords = ["etc.", "i.e", "considered", "information", "documents", "document", "discussing", "discuss",
                         "following", "issues", "identify", "find", "must", "find", "so-called","impact","factor",
                         "shows", "mention", "purpose", "include", "concentrate", "required", "relevant", "relevants"]

        for q in querysDict:
            stringQ = querysDict[q][0]
            queryNoStem = Parse(self.stop_words).parseText(querysDict[q][0])
            if (self.doStem == 1):
                querysDict[q][0] = self.makeStemList(queryNoStem)
            else: querysDict[q][0] = queryNoStem
            querysDict[q][1] = Parse(list(set().union(self.stop_words, destStopWords))).parseText(querysDict[q][1])
            if (self.doStem == 1):
                querysDict[q][1] = self.makeStemList(querysDict[q][1])
            #querysDict[q][1] = set(querysDict[q][1])
            #print(q,": " ,querysDict[q][1])
            querysDict[q][3] = list(set().union(querysDict[q][0], querysDict[q][1]))
            #querysDict[q][3] = querysDict[q][0] + querysDict[q][1]
            if (self.doSemantics == 1):
                semanticQuery = []
                for w in queryNoStem:
                    # queryNoStem
                    if (w.lower() in self.similarityDict):
                        for sim in self.similarityDict[w.lower()]:
                            if (sim[0] not in semanticQuery):
                                semanticQuery.append(sim[0])
                            #print(semanticQuery)
                if(self.doStem == 1):
                    semanticQuery = self.makeStemList(semanticQuery)
                querysDict[q][2] = semanticQuery
                querysDict[q][3] = list(set().union(querysDict[q][3], semanticQuery))
                del semanticQuery
            stop = timeit.default_timer()
            resList = self.ranker.calculateRate(querysDict[q], True)
            tmpDict = {}
            theRanking = []
            if (self.citiesList != None):
                for city in self.citiesList:
                    for doc in resList:
                        if (self.fileIndex[doc][2] == city):
                            tmpDict[doc] = resList[doc]
                    x = itertools.islice(tmpDict.items(), 0, 50)
                    for i in x:
                        theRanking.append(i)
            else:
                x = itertools.islice(resList.items(), 0, 50)
                for doc in x:
                    theRanking.append(doc)
            if (self.showEntities == 1):
                resultDict[(q, stringQ)] = self.addEntities(theRanking)
            else:
                resultDict[(q, stringQ)] = theRanking
        #print(resultDict)
        stop = timeit.default_timer()
        print("### Time to Answer ###", stop - start, "seconds")
        return (resultDict)


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
            # print(entitiesToShow)
            result[tuple] = entitiesToShow
        return result
        # print("FINAL: ", result)

    def makeStemList(self, afterParse):
        ps = PorterStemmer()
        ans = []
        for i in range(0, len(afterParse)):
            tmp = ""
            if (afterParse[i][0].isalpha()):
                if (afterParse[i].isupper()):
                    tmp = ps.stem(afterParse[i])
                    ans.append(tmp.upper())
                    del tmp
                else:
                    ans.append(ps.stem(afterParse[i]))
            continue
        return ans

    def nerrativeMaker(self,queryFile):
        inPart = False
        with open(queryFile, "r+") as querysFile:
            file = querysFile.readlines()
            notList = []
            yesList = []
            Q = {}
            nerrative = ""
            nerRead = False
            for line in file:
                if ("<num>" in line):
                    queryNum = line[line.index('>') + 1:].split(": ")[1].strip()
                elif ("</top>" in line):
                    nerRead = False
                    inPart = True
                elif (nerRead):
                    nerrative += line.lower()
                elif ("<narr>" in line):
                    nerRead = True
                if (inPart):
                    Q[queryNum] = [nerrative, "", ""]
                    inPart = False
                    del nerrative
                    nerrative = ""
            #print(Q)
            for q in Q:
                notList = []
                yesList = []
                if ("relevant:" in Q[q][0]):
                    splitedNer = Q[q][0].split("\n")
                    notRel = False
                    for part in splitedNer:
                        if (
                                "not relevant:" in part or "non-relevant:" in part or "irrlevant:" in part or "non relevant" in part):
                            notRel = True
                            notList.append(part.strip())
                        if (notRel == False):
                            yesList.append(part.strip())
                        elif (notRel):
                            notList.append(part.strip())
                    Q[q][1] = yesList
                    Q[q][2] = notList
                    del yesList
                    del notList
                else:
                    splitedNer = re.sub('[\n]', " ", Q[q][0])
                    splitedNer = re.split('[.]', splitedNer)
                    for part in splitedNer:
                        if (
                                "not relevant" in part or "non-relevant" in part or "irrlevant" in part or "non relevant" in part):
                            notList.append(part.strip())
                        elif ("relevant" in part):
                            yesList.append(part.strip())
                    Q[q][1] = yesList
                    Q[q][2] = notList
                    del yesList
                    del notList
        return Q