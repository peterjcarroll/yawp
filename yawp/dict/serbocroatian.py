import re
from yawp.parser import YAWiktionaryParser

LANG_NAME = 'Serbo-Croatian'
PARTS_OF_SPEECH = ['Verb', 'Noun', 'Adjective', 'Adverb', 'Preposition', 'Interjection', 'Pronoun', 'Conjunction', 'Letter', 'Particle']
INFLECTIONS = ['Conjugation', 'Declension']

_conjugation_regex = re.compile(r"^\|(?P<form>\w+\.\w+)=(?P<inflected_word>.*)$", re.RegexFlag.MULTILINE)

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
                definitions.append(Definition(term.word, headings))
                headings = []
            headings.append(heading)
        elif heading.title in INFLECTIONS:
            headings.append(heading)
    
    if len(headings) > 0:
        definitions.append(Definition(term.word, headings))

    return definitions


class Definition:

    def __init__(self, word, headings):
        self.word = word
        self.headings = headings
        self.part_of_speech = ''
        self.meanings = []
        self.inflection = {}

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

        elif heading.title in INFLECTIONS:
            self.inflection['type'] = heading.title
            if heading.title == 'Conjugation':
                self.parse_conjugation(heading)
            elif heading.title == 'Declension':
                pass # TODO: PJC
    

    def parse_conjugation(self, heading):
        self.inflection['Infinitive'] = self.word

        match_start = -1  
        match_end = -1
        form = ''
        inflected_word = ''
        match = _conjugation_regex.search(heading.text)
        while match:
            if match_start >= 0:
                match_end = match.start() - 1
                self.add_inflection(form, inflected_word)
            match_start = match.start()
            form = match.groupdict()['form']
            inflected_word = match.groupdict()['inflected_word']
            match = _conjugation_regex.search(heading.text, match_start + 1)
        # Don't forget the last match
        if match_start >= 0:
            self.add_inflection(form, inflected_word)

    def add_inflection(self, form, inflected_word):
        #TODO: PJC just discovered that one form here could end up in multiple verb forms in the conjugation table. Need to rework.
        form_name = self.get_inflection_form_name(form)
        self.inflection[form_name] = inflected_word

    def get_inflection_form_name(self, form):
        if form == 'p.va': return 'Past verbal adverb'
        elif form == 'pr.va': return 'Present verbal adverb'           
        elif form == 'pr.1s': return 'First person singular present'
        return form

    def __str__(self):
        return "{0}: {1}".format(self.part_of_speech, self.meanings)