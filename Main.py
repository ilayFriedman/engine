from Searcher import Searcher

searcher = Searcher("/stop_words.txt", "post",False,["Kiev"])
q = searcher.singleQueryCalc("internal multilateral")
#q = searcher.multiQueryCalc("Qtest")