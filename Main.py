import timeit
from collections import defaultdict

import ujson as ujson
from gensim.models import KeyedVectors

from Searcher import Searcher
import gensim.models

# searcher = Searcher("/stop_words.txt", "post",False,True)
# #q = searcher.singleQueryCalc("ilay")
# q = searcher.multiQueryCalc("Qtest")
#


# from gensim.scripts.glove2word2vec import glove2word2vec
# glove2word2vec(glove_input_file='glove.6B.200d.txt', word2vec_output_file="vectorsFile.txt")
#
# model = KeyedVectors.load_word2vec_format('vectorsFile.txt', binary=False)
start = timeit.default_timer()
model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
stop = timeit.default_timer()  ## CLEAR PRINT!
print("~### OPEN MODEL ###~ : ", stop - start, "seconds")
vector = model["car"]

#print (model.similar_by_vector(vector, topn=10, restrict_vocab=None))
ms = model.similar_by_word(vector,4)
stop = timeit.default_timer()  ## CLEAR PRINT!
print("~### get similar ###~ : ", stop - start, "seconds")
for x in ms:
    print(x[0],x[1])


# with open("ppdb-2.0-m-lexical" , "r+") as file:
#     similarityDict = defaultdict(list)
#     for line in file:
#         curr = line.split(" ||| ")
#         word = (curr[1])
#         otherWord = curr[2]
#         score = curr[3].split(" ")[0].split("=")[1]
#         similarityDict[word].append((otherWord,score))
#     with open("simDict.ujson", "w+") as tmpFileDict:
#         ujson.dump(similarityDict, tmpFileDict)
#     print(similarityDict["car"])
#     #print (similarityDict)