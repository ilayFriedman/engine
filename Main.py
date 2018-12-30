import itertools
import timeit
from collections import defaultdict

import ujson as ujson
#from gensim.models import KeyedVectors
from operator import itemgetter

from Searcher import Searcher
#import gensim.models

citiesfile = open("post/S_citiesIndex.ujson", "r+")
baseFile = open("post/S_baseDict.ujson", "r+")
fileFile = open("post/S_fileIndex.ujson", "r+")
ReadCitiesIndex = ujson.load(citiesfile)
ReadBaseDict = ujson.load(baseFile)
ReadFileIndex = ujson.load(fileFile)
citiesfile.close()
baseFile.close()
fileFile.close()

searcher = Searcher("/stop_words.txt", "post", True ,ReadBaseDict,ReadFileIndex,
                    False, True)
#q = searcher.singleQueryCalc("Falkland")
start = timeit.default_timer()
q = searcher.multiQueryCalc("queries.txt")
stop = timeit.default_timer()
print("### Time to Answer ###",stop-start, "seconds")



# with open("ppdb-2.0-m-lexical" , "r+") as file:
#     similarityDict = defaultdict(list)
#     tmp = []
#     for line in file:
#         curr = line.split(" ||| ")
#         word = (curr[1])
#         otherWord = curr[2]
#         score = curr[3].split(" ")[0].split("=")[1]
#         if(float(score) >= 3.7):
#             tmp.append((otherWord,score))
#         x = sorted(tmp, key=itemgetter(1), reverse=True)
#         x = itertools.islice(x, 0, 3)
#         for w in x:
#             similarityDict[word].append(w)
#     with open("simDictM.ujson", "w+") as tmpFileDict: #change to your favorite type of file
#         ujson.dump(similarityDict, tmpFileDict)
#         tmpFileDict.close()
#     print(similarityDict["red"])
#     print (similarityDict)