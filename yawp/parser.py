import re
import requests

_language_regex = re.compile(r"^==(?P<lang>[\w\s\-]+)==$", re.RegexFlag.MULTILINE)
_heading_regex = re.compile(r"^===+(?P<heading>[\w\s\-]+)===+$", re.RegexFlag.MULTILINE)

class Entry:

    def __init__(self, text, search_term):        
        self.terms =[]
        self.search_term = search_term
        self.parse(text)
    
    def parse(self, text):
        match_start = -1   
        match_end = -1
        language = ''
        match = _language_regex.search(text)
        while match:
            if match_start >= 0:
                match_end = match.start() - 1
                self.terms.append(Term(text[match_start:match_end], language, self.search_term))
            match_start = match.start()
            language = match.groupdict()['lang']
            match = _language_regex.search(text, match_start + 1)
        # Don't forget the last match
        if match_start >=0:
            self.terms.append(Term(text[match_start:], language, self.search_term))


class Term:

    def __init__(self, text, language, search_term):
        self.language = language
        self.word = search_term
        self.headings = []        
        #self.parts_of_speech = []
        self.parse(text)

    def parse(self, text):
        #print(self.language)
        #print(self.word)

        match_start = -1  
        match_end = -1
        heading = ''
        match = _heading_regex.search(text)
        while match:
            if match_start >= 0:
                match_end = match.start() - 1
                self.headings.append(Heading(text[match_start:match_end], heading))
            match_start = match.start()
            heading = match.groupdict()['heading']
            match = _heading_regex.search(text, match_start + 1)
        # Don't forget the last match
        if match_start >=0:
            self.headings.append(Heading(text[match_start:], heading))


class Heading:

    def __init__(self, text, title):
        self.title = title
        self.text = text
        #print(text)


class YAWiktionaryParser:

    def __init__(self):
        self.site = 'en'

    def get(self, term):
        r = requests.get('https://{0}.wiktionary.org/wiki/{1}?action=raw'.format(self.site, term))
        if r.status_code == 200:
            return Entry(r.text, term)
        return None

        
        