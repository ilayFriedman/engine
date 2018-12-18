import os
import timeit
from collections import defaultdict, Counter
from nltk.stem import PorterStemmer
import ujson as ujson
from Indexer import Indexer
from Parse import Parse

class ReadFile:
    def __init__(self, pathSurce,pathForPosting):
        self.do_Stemming=False
        self.start = timeit.default_timer()
        self.pathToRead = pathSurce
        self.textCount = 0
        self.indexer = Indexer(pathForPosting)
        self.fileIndex = defaultdict(list)
        self.citiesList = []
        self.langList=[]

        with open(pathSurce+"/stop_words.txt", "r+") as SW:
            self.stop_words = map(str.strip, SW.readlines())
        SW.close()
        self.stop_words = set(self.stop_words)
        self.parser = Parse(self.stop_words)

    def readAllFiles(self):
        i = 0
        j = 0
        countBigMarge = 0
        for root, dirs, files in os.walk(self.pathToRead):
            for file in files:
                with open(os.path.join(root, file), "r") as auto:
                    self.readAllCities(auto,"<F P=104>")
                    auto.close()
        self.citiesList = set(self.citiesList)
        stop = timeit.default_timer()       ## CLEAR PRINT!
        print("~### CITY READ ###~ : ", stop - self.start, "seconds")       ## CLEAR PRINT!

        for root, dirs, files in os.walk(self.pathToRead):
            for file in files:
                with open(os.path.join(root, file), "r") as auto:
                    auto.seek(0)
                    self.breakToParts(auto, "<TEXT>", "</TEXT>", "<DOCNO>","<F P=105>","<F P=104>")
                    auto.close()
                self.indexer.merge()
                self.indexer.tmpDict.clear()
                i = i + 1

            if (countBigMarge == 500):
                self.indexer.bigMerge(j)
                stop = timeit.default_timer()       ## CLEAR PRINT!
                print("~### BIG MERGE ###~ : ", stop - self.start, "seconds")       ## CLEAR PRINT!
                countBigMarge = 0
            countBigMarge = countBigMarge + 1
            j = j + 1
        self.langList = set(self.langList)      ## Making the Lang to set!!
        self.indexer.bigMerge(j)
        stop = timeit.default_timer()       ## CLEAR PRINT!
        print("~### BIG MERGE ###~ : ", stop - self.start, "seconds")       ## CLEAR PRINT!

        stop = timeit.default_timer()       ## CLEAR PRINT!
        print("~### FINAL MERGE ###~ : ", stop - self.start, "seconds")       ## CLEAR PRINT!
        self.indexer.finalMerge()
        if(self.do_Stemming):
            self.indexer.indexMaker("S_finalIndexName")
        else:
            self.indexer.indexMaker("finalIndexName")
        stop = timeit.default_timer()       ## CLEAR PRINT!
        print("~### INDEX MAKER ###~ : ", stop - self.start, "seconds")       ## CLEAR PRINT!

        self.indexer.createCityDict(self.citiesList)
        self.writeAllDictToDisk()

    def breakToParts(self, file, openLabel, closeLabel, subLabel=None, languge=None,subCity=None):
        inPart = False
        stringText = ""
        openSubValue = ""
        subLangValue = ""
        subCityValue = ""

        for line in file:
            if (subLabel != None and subLabel in line):
                openSubValue = line[line.index('>') + 1:-(len(line) - line.index('<', 2))].strip()
            elif (languge != None and languge in line and '><' not in line):
                subLangValue = (line[line.index('>') + 1:-(len(line) - line.index('<', 11))].strip())
            elif (subCity != None and subCity in line and '><' not in line ):
                subCityValue = (line[line.index('>') + 1:-(len(line) - line.index(' ',11))].strip())
            elif (line.strip() == openLabel):
                inPart = True
            elif(line.strip() == closeLabel):
                self.textCount = self.textCount + 1
                inPart = False
                afterParse = self.parser.parseText(stringText)
                if(self.do_Stemming):
                    afterParse = self.makeStemList(afterParse)
                self.indexer.tokenList = afterParse
                self.indexer.add(openSubValue)
                stringText = ""
                self.fileIndex[openSubValue] = [self.indexer.maxTF, len(self.indexer.tokenList),subCityValue,subLangValue]
                self.langList.append(subLangValue)
                continue
            if (inPart):
                stringText += line

    def readAllCities(self, file, subCity): # make allCity list first
        subCityValue = ""
        for line in file:
            if (subCity != None and subCity in line and '><' not in line):
                subCityValue = (line[line.index('>') + 1:-(len(line) - line.index(' ', 11))].strip())
            if (subCityValue != ""):
                self.citiesList.append(subCityValue)
                subCityValue = ""

    def writeAllDictToDisk(self):
        if(self.do_Stemming):
            with open("postings/" + "S_baseDict" + ".ujson", "w+") as base:
                ujson.dump(self.indexer.baseDict, base)
            base.close()
            with open("postings/" + "S_fileIndex" + ".ujson", "w+") as fileIndex:
                ujson.dump(self.fileIndex, fileIndex)
            fileIndex.close()
            with open("postings/" + "S_citiesIndex" + ".ujson", "w+") as cityIndex:
                ujson.dump(self.indexer.citiesIndex, cityIndex)
            cityIndex.close()
        else:
            with open("postings/" + "baseDict" + ".ujson", "w+") as base:
                ujson.dump(self.indexer.baseDict, base)
            base.close()
            with open("postings/" + "fileIndex" + ".ujson", "w+") as fileIndex:
                ujson.dump(self.fileIndex, fileIndex)
            fileIndex.close()
            with open("postings/" + "citiesIndex" + ".ujson", "w+") as cityIndex:
                ujson.dump(self.indexer.citiesIndex, cityIndex)
            cityIndex.close()

    def makeStemList(self, afterParse):
        ps = PorterStemmer()
        for i in range(0,len(afterParse)):
            afterParse[i] = ps.stem(afterParse[i])
        return afterParse
