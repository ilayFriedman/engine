from Searcher import Searcher

searcher = Searcher("/stop_words.txt", "post",False)
#q = searcher.singleQueryCalc("oren shor")
q = searcher.multiQueryCalc("Qtest")