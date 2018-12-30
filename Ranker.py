import re
from collections import Counter, defaultdict, OrderedDict
from operator import itemgetter

import math


class Ranker:
    def __init__(self, baseIndex, docIndex, postPath, doStem):
        self.baseIndex = baseIndex
        self.docIndex = docIndex
        self.postPath = postPath
        self.doStem = doStem
        self.avdl = 0
        for file in self.docIndex:
            self.avdl += float(self.docIndex[file][4])
        self.avdl = self.avdl / len(self.docIndex.keys())
        self.docNum = len(self.docIndex.keys())

    def calculateRate(self,query):
        resultDict = {}
        counter = Counter(query)
        cWD = {}
        for word in query:
            data = self.readFromFile(word)
            if(data != None):
                data = re.sub("[\[\]\"\']", "", data)
                data = data.split(", ")
                inDocList = {}
                i = 0
                while (i < (len(data) - 1)):
                    inDocList[data[i]] = data[i + 1]
                    i += 2
                cWD[word] = inDocList

        for doc in self.docIndex:
            currRankBM25 = 0
            docLen = self.docIndex[doc][4]
            for word in query:
                if(word in self.baseIndex.keys()):
                    currDF = self.baseIndex[word][3]
                else: currDF = 0
                if(word in cWD and cWD[word] != None):
                    if (doc in cWD[word]):
                        currCWD = cWD[word][doc]
                        currRankBM25 += self.bmCalc(counter[word], currCWD, docLen, currDF)
            if(currRankBM25 != 0 ):
                resultDict[doc] = currRankBM25
        bestRank = OrderedDict(sorted(resultDict.items(), key = itemgetter(1), reverse = True))
        return(bestRank)


    def bmCalc(self, cWQ, cWD, docLen, df):
        k = 2.0
        b = 0.75
        res = ((k + 1) * float(cWD)) / (float(cWD) + (k * (1 - b + (b * (float(docLen) / float(self.avdl))))))
        res = res *float(cWQ)
        if(df != 0):
            res = res * math.log10((self.docNum + 1)/df)
        return res

    def readFromFile(self, token):
        indexName = ""
        if (self.doStem == 1):
            indexName = "S_finalIndex"
        else:
            indexName = "finalIndex"
        with open(self.postPath + "/" + indexName + ".txt", "r+") as index:
            data = ""
            if(token in self.baseIndex):
                offset = self.baseIndex[token][0]
                size = self.baseIndex[token][1]
            elif(token.upper() in self.baseIndex):
                offset = self.baseIndex[token.upper()][0]
                size = self.baseIndex[token.upper()][1]
            elif(token.lower() in self.baseIndex):
                offset = self.baseIndex[token.lower()][0]
                size = self.baseIndex[token.lower()][1]
            else:
                return None
            index.seek(offset)
            data = index.read(size)
            return (data)
