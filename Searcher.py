import ujson

from Parse import Parse
from Ranker import Ranker


class Searcher:
    def __init__(self,stopWords,basePath,docPath,doStem):
        if(doStem):
            with open(basePath + "/S_baseDict.ujson", "r+" ) as file:
                baseDic = ujson.load(file)
                file.close()
            with open(docPath + "/S_fileIndex.ujson", "r+" ) as file1:
                fileIndex = ujson.load(file1)
                file1.close()
        else:
            with open(basePath + "/baseDict.ujson", "r+" ) as file:
                baseDic = ujson.load(file)
                file.close()
            with open(docPath + "/fileIndex.ujson", "r+" ) as file1:
                fileIndex = ujson.load(file1)
                file1.close()
        self.ranker = Ranker(baseDic,fileIndex)
        self.stopWords= stopWords

    def singleQueryCalc(self,query):
        parseQuery = Parse(self.stopWords).parseText(query)

