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
        if form == 'p.va': 
            self.inflection['Past verbal adverb'] = inflected_word
        elif form == 'pr.va': 
            self.inflection['Present verbal adverb'] = inflected_word
        elif form == 'pr.1s': 
            self.inflection['First person singular present'] = inflected_word
        elif form == 'pr.2s': 
            self.inflection['Second person singular present'] = inflected_word
        elif form == 'pr.3s': 
            self.inflection['Third person singular present'] = inflected_word
        elif form == 'pr.1p': 
            self.inflection['First person plural present'] = inflected_word
        elif form == 'pr.2p': 
            self.inflection['Second person plural present'] = inflected_word
        elif form == 'pr.3p': 
            self.inflection['Third person plural present'] = inflected_word
        elif form == 'f1.hr': 
            self.inflection['First person singular future I (Croatian)'] = inflected_word + ' ću'
            self.inflection['Second person singular future I (Croatian)'] = inflected_word + ' ćeš'
            self.inflection['Third person singular future I (Croatian)'] = inflected_word + ' će'
            self.inflection['First person plural future I (Croatian)'] = inflected_word + ' ćemo'
            self.inflection['Second person plural future I (Croatian)'] = inflected_word + ' ćete'
            self.inflection['Third person plural future I (Croatian)'] = inflected_word + ' će'
        elif form == 'f1.stem': 
            self.inflection['First person singular future I'] = inflected_word + 'ću'
            self.inflection['Second person singular future I'] = inflected_word + 'ćeš'
            self.inflection['Third person singular future I'] = inflected_word + 'će'
            self.inflection['First person plural future I'] = inflected_word + 'ćemo'
            self.inflection['Second person plural future I'] = inflected_word + 'ćete'
            self.inflection['Third person plural future I'] = inflected_word + 'će'
        elif form == 'impf.1s': 
            self.inflection['First person singular past imperfect'] = inflected_word
        elif form == 'impf.2s': 
            self.inflection['Second person singular past imperfect'] = inflected_word
        elif form == 'impf.3s': 
            self.inflection['Third person singular past imperfect'] = inflected_word
        elif form == 'impf.1p': 
            self.inflection['First person plural past imperfect'] = inflected_word
        elif form == 'impf.2p': 
            self.inflection['Second person plural past imperfect'] = inflected_word
        elif form == 'impf.3p': 
            self.inflection['Third person plural past imperfect'] = inflected_word
        elif form == 'a.1s': 
            self.inflection['First person singular past aorist'] = inflected_word
        elif form == 'a.2s': 
            self.inflection['Second person singular past aorist'] = inflected_word
        elif form == 'a.3s': 
            self.inflection['Third person singular past aorist'] = inflected_word
        elif form == 'a.1p': 
            self.inflection['First person plural past aorist'] = inflected_word
        elif form == 'a.2p': 
            self.inflection['Second person plural past aorist'] = inflected_word
        elif form == 'a.3p': 
            self.inflection['Third person plural past aorist'] = inflected_word
        elif form == 'impt.2s': 
            self.inflection['Second person singular imperative'] = inflected_word
        elif form == 'impt.1p': 
            self.inflection['First person plural imperative'] = inflected_word
        elif form == 'impt.2p': 
            self.inflection['Second person plural imperative'] = inflected_word
        elif form == 'app.ms': 
            self.inflection['Active past participle masculine singular'] = inflected_word
            self.inflection['First person masculine singular future II'] = 'budem ' + inflected_word
            self.inflection['Second person masculine singular future II'] = 'budeš ' + inflected_word
            self.inflection['Third person masculine singular future II'] = 'bude ' + inflected_word
            self.inflection['First person masculine singular past perfect'] = inflected_word + ' sam'
            self.inflection['Second person masculine singular past perfect'] = inflected_word + ' si'
            self.inflection['Third person masculine singular past perfect'] = inflected_word + ' je'
            self.inflection['First person masculine singular past pluperfect'] = 'bio sam ' + inflected_word
            self.inflection['Second person masculine singular past pluperfect'] = 'bio si ' + inflected_word
            self.inflection['Third person masculine singular past pluperfect'] = 'bio je ' + inflected_word
            self.inflection['First person masculine singular conditional I'] = inflected_word + ' bih'
            self.inflection['Second person masculine singular conditional I'] = inflected_word + ' bi'
            self.inflection['Third person masculine singular conditional I'] = inflected_word + ' bi'
            self.inflection['First person masculine singular conditional II'] = 'bio bih ' + inflected_word
            self.inflection['Second person masculine singular conditional II'] = 'bio bi ' + inflected_word
            self.inflection['Third person masculine singular conditional II'] = 'bio bi ' + inflected_word
        elif form == 'app.fs': 
            self.inflection['Active past participle feminine singular'] = inflected_word
            self.inflection['First person feminine singular future II'] = 'budem ' + inflected_word
            self.inflection['Second person feminine singular future II'] = 'budeš ' + inflected_word
            self.inflection['Third person feminine singular future II'] = 'bude ' + inflected_word
            self.inflection['First person feminine singular past perfect'] = inflected_word + ' sam'
            self.inflection['Second person feminine singular past perfect'] = inflected_word + ' si'
            self.inflection['Third person feminine singular past perfect'] = inflected_word + ' je'
            self.inflection['First person feminine singular past pluperfect'] = 'bila sam ' + inflected_word
            self.inflection['Second person feminine singular past pluperfect'] = 'bila si ' + inflected_word
            self.inflection['Third person feminine singular past pluperfect'] = 'bila je ' + inflected_word
            self.inflection['First person feminine singular conditional I'] = inflected_word + ' bih'
            self.inflection['Second person feminine singular conditional I'] = inflected_word + ' bi'
            self.inflection['Third person feminine singular conditional I'] = inflected_word + ' bi'
            self.inflection['First person feminine singular conditional II'] = 'bila bih ' + inflected_word
            self.inflection['Second person feminine singular conditional II'] = 'bila bi ' + inflected_word
            self.inflection['Third person feminine singular conditional II'] = 'bila bi ' + inflected_word
        elif form == 'app.ns': 
            self.inflection['Active past participle neuter singular'] = inflected_word
            self.inflection['First person neuter singular future II'] = 'budem ' + inflected_word
            self.inflection['Second person neuter singular future II'] = 'budeš ' + inflected_word
            self.inflection['Third person neuter singular future II'] = 'bude ' + inflected_word
            self.inflection['First person neuter singular past perfect'] = inflected_word + ' sam'
            self.inflection['Second person neuter singular past perfect'] = inflected_word + ' si'
            self.inflection['Third person neuter singular past perfect'] = inflected_word + ' je'
            self.inflection['First person neuter singular past pluperfect'] = 'bilo sam ' + inflected_word
            self.inflection['Second person neuter singular past pluperfect'] = 'bilo si ' + inflected_word
            self.inflection['Third person neuter singular past pluperfect'] = 'bilo je ' + inflected_word
            self.inflection['First person neuter singular conditional I'] = inflected_word + ' bih'
            self.inflection['Second person neuter singular conditional I'] = inflected_word + ' bi'
            self.inflection['Third person neuter singular conditional I'] = inflected_word + ' bi'
            self.inflection['First person neuter singular conditional II'] = 'bilo bih ' + inflected_word
            self.inflection['Second person neuter singular conditional II'] = 'bilo bi ' + inflected_word
            self.inflection['Third person neuter singular conditional II'] = 'bilo bi ' + inflected_word
        #TODO: more
        # https://en.wiktionary.org/wiki/Template:sh-conj
        # https://en.wiktionary.org/wiki/biti?action=raw
        # https://en.wiktionary.org/wiki/biti#Serbo-Croatian
        

    def __str__(self):
        return "{0}: {1}".format(self.part_of_speech, self.meanings)