import requests

class Entry:

    def __init__(self, text):
        print(text)
        self.terms =[]


class Term:

    def __init__(self):
        self.language = ''
        self.word = ''
        self.headings = []
        self.parts_of_speech = []


class YAWiktionaryParser:

    def __init__(self):
        self.site = 'en'

    def get(self, term):
        r = requests.get('https://{0}.wiktionary.org/wiki/{1}?action=raw'.format(self.site, term))
        if r.status_code == 200:
            entry = Entry(r.text)

        
        