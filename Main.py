import itertools
import timeit
from collections import defaultdict

import ujson as ujson
#from gensim.models import KeyedVectors
from operator import itemgetter

from Searcher import Searcher
#import gensim.models

# citiesfile = open("post/citiesIndex.ujson", "r+")
# baseFile = open("post/baseDict.ujson", "r+")
# fileFile = open("post/fileIndex.ujson", "r+")
# ReadCitiesIndex = ujson.load(citiesfile)
# ReadBaseDict = ujson.load(baseFile)
# ReadFileIndex = ujson.load(fileFile)
# citiesfile.close()
# baseFile.close()
# fileFile.close()
#
# searcher = Searcher("/stop_words.txt", "post", False,ReadBaseDict,ReadFileIndex,
#                     False, False)
# #q = searcher.singleQueryCalc("Falkland")
# start = timeit.default_timer()
# q = searcher.multiQueryCalc("queries.txt")
# stop = timeit.default_timer()
# print("### Time to Answer ###",stop-start, "seconds")



# from gensim.scripts.glove2word2vec import glove2word2vec
# glove2word2vec(glove_input_file='glove.6B.200d.txt', word2vec_output_file="vectorsFile.txt")
#
# model = KeyedVectors.load_word2vec_format('vectorsFile.txt', binary=False)
# start = timeit.default_timer()
# model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
# stop = timeit.default_timer()  ## CLEAR PRINT!
# print("~### OPEN MODEL ###~ : ", stop - start, "seconds")
# vector = model["car"]
#
# #print (model.similar_by_vector(vector, topn=10, restrict_vocab=None))
# ms = model.similar_by_word(vector,4)
# stop = timeit.default_timer()  ## CLEAR PRINT!
# print("~### get similar ###~ : ", stop - start, "seconds")
# for x in ms:
#     print(x[0],x[1])


with open("ppdb-2.0-m-lexical" , "r+") as file:
    similarityDict = defaultdict(list)
    tmp = []
    for line in file:
        curr = line.split(" ||| ")
        word = (curr[1])
        otherWord = curr[2]
        score = curr[3].split(" ")[0].split("=")[1]
        if(float(score) >= 3.7):
            tmp.append((otherWord,score))
        x = sorted(tmp, key=itemgetter(1), reverse=True)
        x = itertools.islice(x, 0, 3)
        for w in x:
            similarityDict[word].append(w)
    with open("simDictM.ujson", "w+") as tmpFileDict: #change to your favorite type of file
        ujson.dump(similarityDict, tmpFileDict)
        tmpFileDict.close()
    print(similarityDict["red"])
    print (similarityDict)