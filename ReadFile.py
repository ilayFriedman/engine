import os
import timeit
from collections import defaultdict, Counter
from nltk.stem import PorterStemmer
import ujson as ujson
from Indexer import Indexer
from Parse import Parse


class ReadFile:
    def __init__(self, pathSurce, pathForPosting):
        self.do_Stemming = False
        self.start = timeit.default_timer()
        self.pathToRead = pathSurce
        self.pathToWrite = pathForPosting
        self.textCount = 0
        self.indexer = Indexer(pathForPosting)
        self.fileIndex = defaultdict(list)
        self.citiesList = []
        self.langList = []
        self.textsList = []

        with open(pathSurce + "/stop_words.txt", "r+") as SW:
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
                    self.readAllCities(auto, "<F P=104>")
                    auto.close()
        self.citiesList = set(self.citiesList)
        stop = timeit.default_timer()  ## CLEAR PRINT!
        print("~### CITY READ ###~ : ", stop - self.start, "seconds")  ## CLEAR PRINT!

        for root, dirs, files in os.walk(self.pathToRead):
            for file in files:
                with open(os.path.join(root, file), "r") as auto:
                    auto.seek(0)
                    self.breakToParts(auto, "<TEXT>", "</TEXT>", "<DOCNO>", "<F P=105>", "<F P=104>")
                    auto.close()
                    self.parseAndIndex()
                self.indexer.merge()
                self.indexer.tmpDict.clear()
                i = i + 1

            if (countBigMarge == 500):
                self.indexer.bigMerge(j)
                stop = timeit.default_timer()  ## CLEAR PRINT!
                print("~### BIG MERGE ###~ : ", stop - self.start, "seconds")  ## CLEAR PRINT!
                countBigMarge = 0
            countBigMarge = countBigMarge + 1
            j = j + 1
        self.langList = set(self.langList)  ## Making the Lang to set!!
        self.indexer.bigMerge(j)
        stop = timeit.default_timer()  ## CLEAR PRINT!
        print("~### BIG MERGE ###~ : ", stop - self.start, "seconds")  ## CLEAR PRINT!

        stop = timeit.default_timer()  ## CLEAR PRINT!
        print("~### FINAL MERGE ###~ : ", stop - self.start, "seconds")  ## CLEAR PRINT!
        self.indexer.finalMerge()
        if (self.do_Stemming):
            self.indexer.indexMaker("S_finalIndex")
        else:
            self.indexer.indexMaker("finalIndex")
        stop = timeit.default_timer()  ## CLEAR PRINT!
        print("~### INDEX MAKER ###~ : ", stop - self.start, "seconds")  ## CLEAR PRINT!

        self.indexer.createCityDict(self.citiesList)
        self.writeAllDictToDisk()

    def breakToParts(self, file, openLabel, closeLabel, subLabel=None, languge=None, subCity=None):
        inPart = False
        stringText = ""
        fileTitle = ""
        fileLang = ""
        fileCity = ""

        for line in file:
            if (subLabel != None and subLabel in line):
                fileTitle = line[line.index('>') + 1:-(len(line) - line.index('<', 2))].strip()
            elif (languge != None and languge in line and '><' not in line):
                fileLang = (line[line.index('>') + 1:-(len(line) - line.index('<', 11))].strip())
            elif (subCity != None and subCity in line and '><' not in line):
                fileCity = (line[line.index('>') + 1:-(len(line) - line.index(' ', 11))].strip())
            elif (line.strip() == openLabel):
                inPart = True
                continue
            elif (line.strip() == closeLabel):
                self.textCount = self.textCount + 1
                inPart = False
                self.textsList.append([stringText,fileTitle,fileCity,fileLang])
                self.langList.append(fileLang)
                stringText = ""
                continue
            if (inPart):
                stringText += line

    def parseAndIndex(self):
        for fileList in self.textsList:
            text = fileList[0]
            title = fileList[1]
            city = fileList[2]
            lang = fileList[3]
            afterParse = self.parser.parseText(text)
            if (self.do_Stemming):
                afterParse = self.makeStemList(afterParse)
            self.indexer.tokenList = afterParse
            entitiesList = self.indexer.add(title)
            self.fileIndex[title] = [self.indexer.maxTF, len(self.indexer.tokenList), city, lang, len(afterParse), entitiesList]
        self.textsList.clear()

    def readAllCities(self, file, subCity):  # make allCity list first
        subCityValue = ""
        for line in file:
            if (subCity != None and subCity in line and '><' not in line):
                subCityValue = (line[line.index('>') + 1:-(len(line) - line.index(' ', 11))].strip())
            if (subCityValue != ""):
                self.citiesList.append(subCityValue)
                subCityValue = ""

    def writeAllDictToDisk(self):
        if (self.do_Stemming):
            with open(self.pathToWrite + "/" + "S_baseDict" + ".ujson", "w+") as base:
                ujson.dump(self.indexer.baseDict, base)
            base.close()
            with open(self.pathToWrite + "/" + "S_fileIndex" + ".ujson", "w+") as fileIndex:
                ujson.dump(self.fileIndex, fileIndex)
            fileIndex.close()
            with open(self.pathToWrite + "/" + "S_citiesIndex" + ".ujson", "w+") as cityIndex:
                ujson.dump(self.indexer.citiesIndex, cityIndex)
            cityIndex.close()
        else:
            with open(self.pathToWrite + "/" + "baseDict" + ".ujson", "w+") as base:
                ujson.dump(self.indexer.baseDict, base)
            base.close()
            with open(self.pathToWrite + "/" + "fileIndex" + ".ujson", "w+") as fileIndex:
                ujson.dump(self.fileIndex, fileIndex)
            fileIndex.close()
            with open(self.pathToWrite + "/" + "citiesIndex" + ".ujson", "w+") as cityIndex:
                ujson.dump(self.indexer.citiesIndex, cityIndex)
            cityIndex.close()

    def makeStemList(self, afterParse):
        ps = PorterStemmer()
        for i in range(0, len(afterParse)):
            if(afterParse[i][0].isalpha()):
                afterParse[i] = ps.stem(afterParse[i])
            continue
        return afterParse
