from .corenlp import StanfordCoreNLP

class Text(object):
    def __init__(self, verbose = False):
        self.Paragraphs = []
        self.Sentences = []
        self.AuthorIds = []
        self.Authors = []
        self.Language = None # TODO: needed? ignored for now. Assuming corenlp does the right thing for the langs we need.
        self.Words = None # TODO: need per sentence words?
        self.Tags = None
        self.Verbose = verbose
        #if self.Language not in [Language.Arabic, Language.English, Language.Spanish]:
        #    raise Exception("Not implemented for language", self.Language)
        return

    def _get_authorid(self, author):
        idx = len(self.Authors)
        if author in self.Authors:
            idx = self.Authors.index(author)
        else:
            self.Authors.append(author)
        return idx

    def getText(self):
        return ' '.join(self.Sentences)

    def cacheWords(self):
        self.Words = []
        self.Tags = []
        chunk_size = 1500 # send chunk_size sentences to the server at a time
        for i in range(0, len(self.Sentences), chunk_size):
            lower = i
            upper = min(len(self.Sentences), i + chunk_size)
            if self.Verbose:
                print("Fetching parse for setences: %d-%d of %d" % (lower, upper, len(self.Sentences)))
            cnlp = StanfordCoreNLP()
            newWords, newTags = cnlp.parse(' '.join(self.Sentences[lower:upper]))
            self.Words += newWords
            self.Tags += newTags

    def getTextTokenizedBySentence(self):
        return self.Sentences

    def getTextTokenizedByWord(self):
        if self.Words is not None:
            return self.Words
        cnlp = StanfordCoreNLP()
        return cnlp.parse(self.getText())[0]
        # TODO: the english tokenizer at least also includes punctuation filtering?

    # def add_untokenized_sentences(self, author, sentences):
    def add_sentences(self, author, sentences):
        """
        Add multiple sentence by an author.
        :param sentences: a list of sentences
        :param author: author name
        """
        idx = self._get_authorid(author)
        for sentence in sentences:
            self.Sentences.append(sentence)
            self.AuthorIds.append(idx)
        if self.Words is not None:
            cnlp = StanfordCoreNLP()
            self.Words += cnlp.parse(sentence)[0]

    def add_sentence(self, author, sentence):
        """
        Add a sentence and corresponding author.
        :param sentence: a single setence
        :param author: author name
        """
        self.add_sentences(author, [sentence])

    def fixed_length_chunk(self, chunk_size):
        """
        Separates text into chunks of 'chunk_size' sentences.
        :param chunk_size: the number of sentences in each chunk
        :return: a tuple (list of lists of sentence indices per chunk, list of list of sentences per chunk)
        ( [ [0, 1, 2], [3,4] ], [ ['sen1', 'sen2', 'sen3'], ['sen4', 'sen5'] ])
        """
        if chunk_size <= 0:
            raise Exception('Invalid chunk size.')

        chunkSentences = []
        chunkSentenceIds = []

        for i in range(0, len(self.Sentences), chunk_size):
            chunkSentences.append(self.Sentences[i:min(len(self.Sentences), i + chunk_size)])
            chunkSentenceIds.append(list( range(i, min(len(self.Sentences), i + chunk_size))))
        return (chunkSentenceIds, chunkSentences)

    def getAuthorForSentenceIndex(self, sentenceIdx):
        return self.Authors[self.AuthorIds[sentenceIdx]]

    def getAuthorIndexForSentence(self, sentenceIdx):
        return self.AuthorIds[sentenceIdx]

    def getAuthorForAuthorIndex(self, authorIdx):
        return self.Authors[authorIdx]

    def writeToFile(self, fname):
        """
        :param fname: File name to write this text object to.
        """
        with open(fname, 'wb') as f:
            import pickle
            pickle.dump(self, f)

    @staticmethod
    def loadFromFile(fname, verbose = False):
        """
        :param fname: File name to read a Text object from.
        :return: the read Text object.
        """
        with open(fname, 'rb') as f:
            import pickle
            text = pickle.load(f)
            text.Verbose = verbose
            return text
