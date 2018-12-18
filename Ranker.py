class Ranker:
    def __init__(self,baseIndex,docIndex):
        self.query = None
        self.baseIndex = baseIndex
        self.docIndex = docIndex

    def calculateRate(self,query):
        self.query = query


