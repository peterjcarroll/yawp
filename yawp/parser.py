import re
import requests

_language_regex = re.compile(r"^==(?P<lang>[\w\s\-]+)==$", re.RegexFlag.MULTILINE)

class Entry:

    def __init__(self, text, search_term):        
        self.terms =[]
        self.search_term = search_term
        self.parse(text)
    
    def parse(self, text):
        match_start = 0        
        match_end = 0
        language = ''
        match = _language_regex.search(text)
        while match:
            if match_start:
                match_end = match.start() - 1
                self.terms.append(Term(text[match_start:match_end], language, self.search_term))
            match_start = match.start()
            language = match.groupdict()['lang']
            match = _language_regex.search(text, match_start + 1)


class Term:

    def __init__(self, text, language, search_term):
        self.language = language
        self.word = search_term
        self.headings = []
        self.parts_of_speech = []
        self.parse(text)

    def parse(self, text):
        print(self.language)
        print(self.word)
        print(text)
        #TODO: here

class YAWiktionaryParser:

    def __init__(self):
        self.site = 'en'

    def get(self, term):
        r = requests.get('https://{0}.wiktionary.org/wiki/{1}?action=raw'.format(self.site, term))
        if r.status_code == 200:
            return Entry(r.text, term)
        return None

        
        