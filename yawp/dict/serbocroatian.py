from yawp.parser import YAWiktionaryParser

LANG_NAME = 'Serbo-Croatian'
PARTS_OF_SPEECH = ['Verb', 'Noun', 'Adjective', 'Adverb', 'Preposition', 'Interjection', 'Pronoun', 'Conjunction', 'Letter', 'Particle']
INFLECTIONS = ['Conjugation', 'Declension']

def get(word):
    p = YAWiktionaryParser()
    entry = p.get(word)
    if entry:
        for term in entry.terms:
            if term.language == LANG_NAME:
                return parse_term(term)
    return None

def parse_term(term):
    definitions = []
    headings = []

    for heading in term.headings:
        if heading.title in PARTS_OF_SPEECH:
            if len(headings) > 0:
                definitions.append(Definition(headings))
                headings = []
            headings.append(heading)
        elif heading.title in INFLECTIONS:
            headings.append(heading)
    
    if len(headings) > 0:
        definitions.append(Definition(headings))

    return definitions


class Definition:

    def __init__(self, headings):
        self.headings = headings
        self.part_of_speech = ''
        self.meanings = []

        for heading in self.headings:
            self.parse_heading(heading)
    
    def parse_heading(self, heading):
        if heading.title in PARTS_OF_SPEECH:
            self.part_of_speech = heading.title
            lines = heading.text.splitlines()
            for line in lines:
                if line.strip().startswith('#'):
                    #TODO: PJC clean up line
                    self.meanings.append(line)
        #TODO: PJC inflection tables

    def __str__(self):
        return "{0}: {1}".format(self.part_of_speech, self.meanings)