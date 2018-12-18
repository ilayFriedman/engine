from Parse import Parse


class Searcher:
    def __init__(self,query,stopWord):
        self.originalQuery = query
        self.parseQuery = Parse(stopWord).parseText(query)

