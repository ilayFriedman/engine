import operator

import requests
import ujson
import os
from collections import Counter, defaultdict

from Parse import Parse


class Indexer:
    def __init__(self, pathToPosting):
        self.pathToWrite = pathToPosting
        self.baseDict = {}
        self.tmpDict = []
        self.dictOfFiles = []
        self.tokenList = []
        self.numCount = {}
        self.citiesIndex = defaultdict(list)
        self.maxTF = 0
        self.numbersOfCapital = 0

    def add(self, fileName):
        entitiesList={}
        currDict = defaultdict(list)
        # tokenSet = set(firstPlace)
        self.numCount = Counter(self.tokenList)
        self.tokenList = set(self.tokenList)
        if (len(self.numCount) > 0):
            self.maxTF = max(self.numCount.items(), key=operator.itemgetter(1))[0]
        else:
            self.maxTF = 0

        for token in self.tokenList:
            if (token == ''):
                continue

            if (token in self.baseDict):
                self.baseDict[token][2] = self.baseDict[token][2] + self.numCount[token]
                if (token in currDict and currDict[token][(len(currDict[token])) - 1][0] == fileName):
                    currDict[token][(len(currDict[token])) - 1][1] = int(
                        currDict[token][(len(currDict[token])) - 1][1]) + self.numCount[token]
                else:
                    currDict[token].append([fileName, self.numCount[token]])
                if (token[0].isupper()):
                    if (token.upper() in entitiesList):
                        entitiesList[token.upper()] += self.numCount[token]
                    else:
                        entitiesList[token.upper()] = self.numCount[token]
            else:
                if (token.lower() in self.baseDict):
                    self.baseDict[token.lower()][2] = self.baseDict[token.lower()][2] + self.numCount[token]
                    if (token in currDict):
                        currDict[token.lower()] = currDict[token]
                        del currDict[token]
                        currDict[token.lower()].append([fileName, self.numCount[token]])
                    elif (token.lower() in currDict):
                        lastPair = (len(currDict[token.lower()])) - 1
                        lastDoc = currDict[token.lower()][lastPair][0]
                        if (lastDoc == fileName):
                            currDict[token.lower()][lastPair][1] = int(currDict[token.lower()][lastPair][1]) + \
                                                                   self.numCount[token]
                        else:
                            currDict[token.lower()].append([fileName, self.numCount[token]])
                    else:
                        currDict[token.lower()].append([fileName, self.numCount[token]])
                else:
                    if (token.upper() in self.baseDict):
                        if(token[0].isupper()):
                            if(token.upper() in entitiesList):
                                entitiesList[token.upper()] += self.numCount[token]
                            else:
                                entitiesList[token.upper()] = self.numCount[token]
                            self.baseDict[token.upper()][2] = self.baseDict[token.upper()][2] + self.numCount[token]
                            if (token.upper() in currDict):
                                lastPair = (len(currDict[token.upper()])) - 1
                                lastDoc = currDict[token.upper()][lastPair][0]
                                if (lastDoc == fileName):
                                    currDict[token.upper()][lastPair][1] = int(currDict[token.upper()][lastPair][1]) + \
                                                                           self.numCount[token]
                                else:
                                    currDict[token.upper()].append([fileName, self.numCount[token]])
                            else:
                                currDict[token.upper()].append([fileName, self.numCount[token]])
                        else:
                            self.baseDict[token.lower()] = self.baseDict[token.upper()]
                            del self.baseDict[token.upper()]
                            self.baseDict[token.lower()][2] = self.baseDict[token.lower()][2] + self.numCount[token]
                            if (token.upper() in currDict):
                                currDict[token.lower()] = currDict[token.upper()]
                                del currDict[token.upper()]
                                lastPair = (len(currDict[token.lower()])) - 1
                                lastDoc = currDict[token.lower()][lastPair][0]
                                if (lastDoc == fileName):
                                    currDict[token.lower()][lastPair][1] = int(currDict[token.lower()][lastPair][1]) + \
                                                                           self.numCount[token]
                                else:
                                    currDict[token.lower()].append([fileName, self.numCount[token]])
                            else:
                                    currDict[token.lower()].append([fileName, self.numCount[token]])
                    else:       ## new word !
                        if (token[0].islower() or token[0].isdigit() or token[1:].isdigit()):
                            self.baseDict[token.lower()] = [-1, -1, self.numCount[token], -1]
                            currDict[token.lower()].append([fileName, self.numCount[token]])
                        elif (token[0].isupper() or token[0].isdigit() or token[1:].isdigit()): ## big word
                            self.baseDict[token.upper()] = [-1, -1, self.numCount[token], -1]
                            currDict[token.upper()].append([fileName, self.numCount[token]])
                            if (token[0].isupper()):
                                entitiesList[token.upper()] = self.numCount[token]
        self.tmpDict.append(currDict)
        return entitiesList

    def merge(self):
        result_dict = {}
        for d in self.tmpDict:
            for k, v in d.items():
                result_dict.setdefault(k, []).extend(v)
        self.dictOfFiles.append(result_dict)

    def bigMerge(self, num):
        result_dict = {}
        for d in self.dictOfFiles:
            for k, v in d.items():
                if (k in self.baseDict):
                    result_dict.setdefault(k, []).extend(v)
                elif (k.lower() in self.baseDict):
                    result_dict.setdefault(k.lower(), []).extend(v)

        keys = sorted(result_dict.keys())
        keys.sort(key=str.casefold)
        letter = keys[0][0]
        dict = {}
        i = 0
        while (i < len(keys)):
            if (letter.lower() == keys[i][0].lower()):
                dict[keys[i]] = result_dict[keys[i]]
                i += 1
            elif (len(dict.items()) != 0):
                with open(self.pathToWrite + "/" + letter + str(num) + ".ujson", "w+") as tmpFileDict:
                    ujson.dump(dict, tmpFileDict)
                    dict.clear()
                tmpFileDict.close()
                if (i < len(keys)):
                    letter = keys[i][0]
        with open(self.pathToWrite + "/" + letter + str(num) + ".ujson", "w+") as tmpFileDict:
            ujson.dump(dict, tmpFileDict)
            dict.clear()
        tmpFileDict.close()
        self.dictOfFiles.clear()

    def finalMerge(self):
        filesNames = sorted(os.listdir(self.pathToWrite + "/"))
        filesNames.sort(key=str.casefold)

        getAtLeastOnce = False
        # for letter in string.ascii_uppercase + string.digits:
        dict = []
        letter = filesNames[0][0]
        i = 0

        while (i < len(filesNames)):
            if (letter.lower() == filesNames[i][0].lower()):
                getAtLeastOnce = True
                fileName = filesNames[i]
                with open(self.pathToWrite + "/" + fileName, "r+") as file:
                    dict.append(ujson.load(file))
                    file.close()
                    os.remove(self.pathToWrite + "/" + fileName)
                    file.close()
                    # filesNames.remove(fileName)
                    i += 1
            elif (getAtLeastOnce):
                result_dict = {}
                for d in dict:
                    for k, v in d.items():
                        result_dict.setdefault(k, []).extend(v)
                with open(self.pathToWrite + "/" + str(letter).upper() + ".ujson", "w+") as tmpFileDict:
                    ujson.dump(result_dict, tmpFileDict)
                dict = []
                result_dict.clear()
                if (i < len(filesNames)):
                    letter = filesNames[i][0]
                getAtLeastOnce = False
                tmpFileDict.close()
        result_dict = {}
        for d in dict:
            for k, v in d.items():
                result_dict.setdefault(k, []).extend(v)
        with open(self.pathToWrite + "/" + str(letter).upper() + ".ujson", "w+") as tmpFileDict:
            ujson.dump(result_dict, tmpFileDict)
            tmpFileDict.close()
        result_dict.clear()

    def indexMaker(self, finalIndexName):
        self.finalIndexName = finalIndexName
        filesNames = sorted(os.listdir(self.pathToWrite + "/"))
        if (len((filesNames)) > 0):
            finalFile = open(self.pathToWrite + "/" + finalIndexName + ".txt", "a+")
        for file in filesNames:
            tempDict = {}
            with open(self.pathToWrite + "/" + file, "r+") as Jfile:
                tempDict = ujson.load(Jfile)
            Jfile.close()
            os.remove(self.pathToWrite + "/" + str(file))
            for item in tempDict:
                begin = int(finalFile.tell())
                if (item in self.baseDict):
                    value = tempDict[item]
                    fileNum = len(value)
                    self.baseDict[item][3] = fileNum
                    self.baseDict[item][0] = begin
                    finalFile.write(str(tempDict[item]))
                    end = int(finalFile.tell())
                    self.baseDict[item][1] = end - begin

        # print(self.baseDict)
        finalFile.close()

    def readFromFile(self, token):
        offset = self.baseDict[token][0]
        size = self.baseDict[token][1]
        with open(self.pathToWrite + "/" + self.finalIndexName + ".txt", "r+") as index:
            index.seek(offset)
            data = index.read(size)  # if you only wanted to read 512 bytes, do .read(512)
            return (data)

    def createCityDict(self, citiesList):
        r = requests.get("https://restcountries.eu/rest/v2/all?fields=capital;name;population;currencies")
        apiDict = ujson.loads(r.content)
        for city in set(citiesList):
            detailsList = ""
            if (city in self.baseDict):
                detailsList = str(self.readFromFile(city))
            elif (city.upper() in self.baseDict):
                detailsList = str(self.readFromFile(city.upper()))
            elif (city.lower() in self.baseDict):
                detailsList = str(self.readFromFile(city.lower()))
            if(len(city) > 1):
                cityName = city[0] + city[1:].lower()
            for i in range(0, len(apiDict)):
                if (cityName in apiDict[i]["capital"]):
                    self.NumbersOfCapitals = self.numbersOfCapital + 1
                    population = apiDict[i]["population"]
                    if (((population) >= 1000 and (population) < 1000000)):
                        population = str(float(population) / 1000) + "K"  # 1,000
                    elif ((population) >= 1000000 and (population) < 1000000000):
                        population = str(float(population) / 1000000) + "M"  # 1,000,000
                    elif ((population) >= 1000000000):
                        population = str(float(population) / 1000000000) + "B"  # 1,000,000,000
                    self.citiesIndex[cityName].append(
                        (apiDict[i]["name"], apiDict[i]["currencies"][0]["code"], population))
            self.citiesIndex[cityName].append(detailsList)
