from Searcher import Searcher
# import gensim.models

searcher = Searcher("/stop_words.txt", "post",False,True)
#q = searcher.singleQueryCalc("ilay")
q = searcher.multiQueryCalc("Qtest")


#
# model = "./WebVectors/3/enwiki_5_ner.txt"
#
# word_vectors = gensim.models.KeyedVectors.load_word2vec_format(model, binary=False)
# print(word_vectors.most_similar("vacation_NOUN"))
# print(word_vectors.most_similar(positive=['woman_NOUN', 'king_NOUN'], negative=['man_NOUN']))