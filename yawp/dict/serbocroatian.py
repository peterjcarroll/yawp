import json
import re
from yawp.parser import YAWiktionaryParser, Template

LANG_NAME = 'Serbo-Croatian'
PARTS_OF_SPEECH = ['Verb', 'Noun', 'Adjective', 'Adverb', 'Preposition', 'Interjection', 'Pronoun', 'Conjunction', 'Letter', 'Particle', 'Proper Noun']
INFLECTIONS = ['Conjugation', 'Declension']
NOUN_CASES = ['Nominative', 'Genitive', 'Dative', 'Accusative', 'Vocative', 'Locative', 'Instrumental']

_inflection_template_regex = re.compile(r"{{(?P<template_name>[\w\-]+)(?P<params>(\|([\w\-\=]+))*)}}", re.RegexFlag.MULTILINE)

_conjugation_regex = re.compile(r"^\|(?P<form>\w+\.\w+)=(?P<inflected_word>.*)$", re.RegexFlag.MULTILINE)
_noun_declension_regex = re.compile(r"\|(?P<inflected_word1>.*?)\|(?P<inflected_word2>.*)$", re.RegexFlag.MULTILINE)
_adj_full_declension_regex = re.compile(r"sh-adj-full\|(?P<root1>\w+)\|\w+\|(?P<root2>\w+)\|\w+", re.RegexFlag.MULTILINE)
_adj_def_declension_regex = re.compile(r"sh-adj-def\|(?P<root>\w+)\|\w+", re.RegexFlag.MULTILINE)
_adj_defindef_declension_regex = re.compile(r"sh-adj-defindef\|(?P<root>\w+)\|\w+", re.RegexFlag.MULTILINE)
#TODO: PJC There are other declension templates, see https://en.wiktionary.org/wiki/Category:Serbo-Croatian_declension-table_templates

def get(word):
    p = YAWiktionaryParser()
    entry = p.get(word)
    if entry:
        for term in entry.terms:
            if term.language == LANG_NAME:
                return parse_term(term)
    return None

def get_json(word):
    defs = get(word)
    if defs:
        json_defs = "["
        for d in defs:
            json_defs += d.toJSON() + ","
        json_defs = json_defs.rstrip(",")
        json_defs += "]"
        return json_defs
    return ""


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
        #TODO: I would like to grab Derived terms and Related terms later as well.
    
    if len(headings) > 0:
        definitions.append(Definition(term.word, headings))

    return definitions


class Definition:

    def __init__(self, word, headings):
        self.word = word
        #self.headings = headings
        self.part_of_speech = ''
        self.meanings = []
        self.inflection = {}

        for heading in headings:
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
                if self.part_of_speech == 'Noun':
                    self.parse_noun_declension(heading)
                elif self.part_of_speech == 'Adjective':
                    self.parse_adj_declension(heading)
                elif self.part_of_speech == 'Pronoun':
                    pass #TODO:
                else:
                    pass # TODO: log unknown declension type
    

    def parse_adj_declension(self, heading):
        self.inflection = Inflection(self.word, heading)
        # match = _adj_full_declension_regex.search(heading.text)
        # if match:
        #     self.parse_adj_full_declension(match.groupdict()['root1'],match.groupdict()['root2'])
        # else:
        #     match = _adj_def_declension_regex.search(heading.text)
        #     if match:
        #         self.parse_adj_def_declension(match.groupdict()['root'])
        #     else:
        #         match = _adj_defindef_declension_regex.search(heading.text)
        #         if match:
        #             self.parse_adj_defindef_declension(match.groupdict()['root'])
        #     #TODO: more else

    
    def parse_adj_full_declension(self, root1, root2):
        self.parse_adj_indef_declension(root1)
        self.parse_adj_def_declension(root1)
        self.parse_adj_comparative_declension(root2)
        #TODO: superlative

    
    def parse_adj_defindef_declension(self, root):
        self.parse_adj_indef_declension(root)
        self.parse_adj_def_declension(root)        

    
    def parse_adj_indef_declension(self, root):
        self.inflection['Indefinite nominative masculine singular'] = self.word
        self.inflection['Indefinite nominative feminine singular'] = root + 'a'
        self.inflection['Indefinite nominative neuter singular'] = root + 'o'
        self.inflection['Indefinite genitive masculine singular'] = root + 'a'
        self.inflection['Indefinite genitive feminine singular'] = root + 'e'
        self.inflection['Indefinite genitive neuter singular'] = root + 'a'
        self.inflection['Indefinite dative masculine singular'] = root + 'u'
        self.inflection['Indefinite dative feminine singular'] = root + 'oj'
        self.inflection['Indefinite dative neuter singular'] = root + 'u'
        self.inflection['Indefinite accusative masculine inanimate singular'] = self.word
        self.inflection['Indefinite accusative feminine singular'] = root + 'u'
        self.inflection['Indefinite accusative neuter singular'] = root + 'o'
        self.inflection['Indefinite accusative masculine animate singular'] = root + 'a'
        self.inflection['Indefinite vocative masculine singular'] = self.word
        self.inflection['Indefinite vocative feminine singular'] = root + 'a'
        self.inflection['Indefinite vocative neuter singular'] = root + 'o'
        self.inflection['Indefinite locative masculine singular'] = root + 'u'
        self.inflection['Indefinite locative feminine singular'] = root + 'oj'
        self.inflection['Indefinite locative neuter singular'] = root + 'u'
        self.inflection['Indefinite instrumental masculine singular'] = root + 'im'
        self.inflection['Indefinite instrumental feminine singular'] = root + 'om'
        self.inflection['Indefinite instrumental neuter singular'] = root + 'im'
        self.inflection['Indefinite nominative masculine plural'] = root + 'i'
        self.inflection['Indefinite nominative feminine plural'] = root + 'e'
        self.inflection['Indefinite nominative neuter plural'] = root + 'a'
        self.inflection['Indefinite genitive masculine plural'] = root + 'ih'
        self.inflection['Indefinite genitive feminine plural'] = root + 'ih'
        self.inflection['Indefinite genitive neuter plural'] = root + 'ih'
        self.inflection['Indefinite dative masculine plural'] = root + 'im(a)'
        self.inflection['Indefinite dative feminine plural'] = root + 'im(a)'
        self.inflection['Indefinite dative neuter plural'] = root + 'im(a)'
        self.inflection['Indefinite accusative masculine plural'] = root + 'e'
        self.inflection['Indefinite accusative feminine plural'] = root + 'e'
        self.inflection['Indefinite accusative neuter plural'] = root + 'a'
        self.inflection['Indefinite vocative masculine plural'] = root + 'i'
        self.inflection['Indefinite vocative feminine plural'] = root + 'e'
        self.inflection['Indefinite vocative neuter plural'] = root + 'a'
        self.inflection['Indefinite locative masculine plural'] = root + 'im(a)'
        self.inflection['Indefinite locative feminine plural'] = root + 'im(a)'
        self.inflection['Indefinite locative neuter plural'] = root + 'im(a)'
        self.inflection['Indefinite instrumental masculine plural'] = root + 'im(a)'
        self.inflection['Indefinite instrumental feminine plural'] = root + 'im(a)'
        self.inflection['Indefinite instrumental neuter plural'] = root + 'im(a)'

    

    def parse_adj_def_declension(self, root):
        self.inflection['Definite nominative masculine singular'] = root + 'i'
        self.inflection['Definite nominative feminine singular'] = root + 'a'
        self.inflection['Definite nominative neuter singular'] = root + 'o'
        self.inflection['Definite genitive masculine singular'] = root + 'og(a)'
        self.inflection['Definite genitive feminine singular'] = root + 'e'
        self.inflection['Definite genitive neuter singular'] = root + 'og(a)'
        self.inflection['Definite dative masculine singular'] = root + 'om(u)'
        self.inflection['Definite dative feminine singular'] = root + 'oj'
        self.inflection['Definite dative neuter singular'] = root + 'om(u)'
        self.inflection['Definite accusative masculine inanimate singular'] = root + 'i'
        self.inflection['Definite accusative masculine animate singular'] = root + 'og(a)'
        self.inflection['Definite accusative feminine singular'] = root + 'u'
        self.inflection['Definite accusative neuter singular'] = root + 'o'
        self.inflection['Definite vocative masculine singular'] = root + 'i'
        self.inflection['Definite vocative feminine singular'] = root + 'a'
        self.inflection['Definite vocative neuter singular'] = root + 'o'
        self.inflection['Definite locative masculine singular'] = root + 'om(u)'
        self.inflection['Definite locative feminine singular'] = root + 'oj'
        self.inflection['Definite locative neuter singular'] = root + 'om(u)'
        self.inflection['Definite instrumental masculine singular'] = root + 'im'
        self.inflection['Definite instrumental feminine singular'] = root + 'om'
        self.inflection['Definite instrumental neuter singular'] = root + 'im'
        self.inflection['Definite nominative masculine plural'] = root + 'i'
        self.inflection['Definite nominative feminine plural'] = root + 'e'
        self.inflection['Definite nominative neuter plural'] = root + 'a'
        self.inflection['Definite genitive masculine plural'] = root + 'ih'
        self.inflection['Definite genitive feminine plural'] = root + 'ih'
        self.inflection['Definite genitive neuter plural'] = root + 'ih'
        self.inflection['Definite dative masculine plural'] = root + 'im(a)'
        self.inflection['Definite dative feminine plural'] = root + 'im(a)'
        self.inflection['Definite dative neuter plural'] = root + 'im(a)'
        self.inflection['Definite accusative masculine plural'] = root + 'e'
        self.inflection['Definite accusative feminine plural'] = root + 'e'
        self.inflection['Definite accusative neuter plural'] = root + 'a'
        self.inflection['Definite vocative masculine plural'] = root + 'i'
        self.inflection['Definite vocative feminine plural'] = root + 'e'
        self.inflection['Definite vocative neuter plural'] = root + 'a'
        self.inflection['Definite locative masculine plural'] = root + 'im(a)'
        self.inflection['Definite locative feminine plural'] = root + 'im(a)'
        self.inflection['Definite locative neuter plural'] = root + 'im(a)'
        self.inflection['Definite instrumental masculine plural'] = root + 'im(a)'
        self.inflection['Definite instrumental feminine plural'] = root + 'im(a)'
        self.inflection['Definite instrumental neuter plural'] = root + 'im(a)'


    def parse_adj_comparative_declension(self, root):
        self.inflection['Comparative nominative masculine singular'] = root + 'i'
        self.inflection['Comparative nominative feminine singular'] = root + 'a'
        self.inflection['Comparative nominative neuter singular'] = root + 'o'
        self.inflection['Comparative genitive masculine singular'] = root + 'og(a)'
        self.inflection['Comparative genitive feminine singular'] = root + 'e'
        self.inflection['Comparative genitive neuter singular'] = root + 'og(a)'
        self.inflection['Comparative dative masculine singular'] = root + 'om(u)'
        self.inflection['Comparative dative feminine singular'] = root + 'oj'
        self.inflection['Comparative dative neuter singular'] = root + 'om(u)'
        self.inflection['Comparative accusative masculine inanimate singular'] = root + 'i'
        self.inflection['Comparative accusative feminine singular'] = root + 'u'
        self.inflection['Comparative accusative neuter singular'] = root + 'o'
        self.inflection['Comparative accusative masculine animate singular'] = root + 'og(a)'
        self.inflection['Comparative vocative masculine singular'] = root + 'i'
        self.inflection['Comparative vocative feminine singular'] = root + 'a'
        self.inflection['Comparative vocative neuter singular'] = root + 'o'
        self.inflection['Comparative locative masculine singular'] = root + 'om(u)'
        self.inflection['Comparative locative feminine singular'] = root + 'oj'
        self.inflection['Comparative locative neuter singular'] = root + 'om(u)'
        self.inflection['Comparative instrumental masculine singular'] = root + 'im'
        self.inflection['Comparative instrumental feminine singular'] = root + 'om'
        self.inflection['Comparative instrumental neuter singular'] = root + 'im'
        self.inflection['Comparative nominative masculine plural'] = root + 'i'
        self.inflection['Comparative nominative feminine plural'] = root + 'e'
        self.inflection['Comparative nominative neuter plural'] = root + 'a'
        self.inflection['Comparative genitive masculine plural'] = root + 'ih'
        self.inflection['Comparative genitive feminine plural'] = root + 'ih'
        self.inflection['Comparative genitive neuter plural'] = root + 'ih'
        self.inflection['Comparative dative masculine plural'] = root + 'im(a)'
        self.inflection['Comparative dative feminine plural'] = root + 'im(a)'
        self.inflection['Comparative dative neuter plural'] = root + 'im(a)'
        self.inflection['Comparative accusative masculine plural'] = root + 'e'
        self.inflection['Comparative accusative feminine plural'] = root + 'e'
        self.inflection['Comparative accusative neuter plural'] = root + 'a'
        self.inflection['Comparative vocative masculine plural'] = root + 'i'
        self.inflection['Comparative vocative feminine plural'] = root + 'e'
        self.inflection['Comparative vocative neuter plural'] = root + 'a'
        self.inflection['Comparative locative masculine plural'] = root + 'im(a)'
        self.inflection['Comparative locative feminine plural'] = root + 'im(a)'
        self.inflection['Comparative locative neuter plural'] = root + 'im(a)'
        self.inflection['Comparative instrumental masculine plural'] = root + 'im(a)'
        self.inflection['Comparative instrumental feminine plural'] = root + 'im(a)'
        self.inflection['Comparative instrumental neuter plural'] = root + 'im(a)'



    def parse_noun_declension(self, heading):
        lines = heading.text.splitlines()
        match_count = 0
        for line in lines:
            match = _noun_declension_regex.search(line)
            if match:
                self.inflection[NOUN_CASES[match_count] + ' singular'] = match.groupdict()['inflected_word1']
                self.inflection[NOUN_CASES[match_count] + ' plural'] = match.groupdict()['inflected_word2']
                match_count += 1


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
        elif form == 'vn':
            self.inflection['Verbal noun'] = inflected_word
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
        elif form == 'app.mp': 
            self.inflection['Active past participle masculine plural'] = inflected_word
            self.inflection['First person masculine plural future II'] = 'budemo ' + inflected_word
            self.inflection['Second person masculine plural future II'] = 'budete ' + inflected_word
            self.inflection['Third person masculine plural future II'] = 'budu ' + inflected_word
            self.inflection['First person masculine plural past perfect'] = inflected_word + ' smo'
            self.inflection['Second person masculine plural past perfect'] = inflected_word + ' ste'
            self.inflection['Third person masculine plural past perfect'] = inflected_word + ' su'
            self.inflection['First person masculine plural past pluperfect'] = 'bili smo ' + inflected_word
            self.inflection['Second person masculine plural past pluperfect'] = 'bili ste ' + inflected_word
            self.inflection['Third person masculine plural past pluperfect'] = 'bili su ' + inflected_word
            self.inflection['First person masculine plural conditional I'] = inflected_word + ' bismo'
            self.inflection['Second person masculine plural conditional I'] = inflected_word + ' biste'
            self.inflection['Third person masculine plural conditional I'] = inflected_word + ' bi'
            self.inflection['First person masculine plural conditional II'] = 'bili bismo ' + inflected_word
            self.inflection['Second person masculine plural conditional II'] = 'bili biste ' + inflected_word
            self.inflection['Third person masculine plural conditional II'] = 'bili bi ' + inflected_word
        elif form == 'app.fp': 
            self.inflection['Active past participle feminine plural'] = inflected_word
            self.inflection['First person feminine plural future II'] = 'budemo ' + inflected_word
            self.inflection['Second person feminine plural future II'] = 'budete ' + inflected_word
            self.inflection['Third person feminine plural future II'] = 'budu ' + inflected_word
            self.inflection['First person feminine plural past perfect'] = inflected_word + ' smo'
            self.inflection['Second person feminine plural past perfect'] = inflected_word + ' ste'
            self.inflection['Third person feminine plural past perfect'] = inflected_word + ' su'
            self.inflection['First person feminine plural past pluperfect'] = 'bile smo ' + inflected_word
            self.inflection['Second person feminine plural past pluperfect'] = 'bile ste ' + inflected_word
            self.inflection['Third person feminine plural past pluperfect'] = 'bile su ' + inflected_word
            self.inflection['First person feminine plural conditional I'] = inflected_word + ' bismo'
            self.inflection['Second person feminine plural conditional I'] = inflected_word + ' biste'
            self.inflection['Third person feminine plural conditional I'] = inflected_word + ' bi'
            self.inflection['First person feminine plural conditional II'] = 'bile bismo ' + inflected_word
            self.inflection['Second person feminine plural conditional II'] = 'bile biste ' + inflected_word
            self.inflection['Third person feminine plural conditional II'] = 'bile bi ' + inflected_word
        elif form == 'app.np': 
            self.inflection['Active past participle neuter plural'] = inflected_word
            self.inflection['First person neuter plural future II'] = 'budemo ' + inflected_word
            self.inflection['Second person neuter plural future II'] = 'budete ' + inflected_word
            self.inflection['Third person neuter plural future II'] = 'budu ' + inflected_word
            self.inflection['First person neuter plural past perfect'] = inflected_word + ' smo'
            self.inflection['Second person neuter plural past perfect'] = inflected_word + ' ste'
            self.inflection['Third person neuter plural past perfect'] = inflected_word + ' su'
            self.inflection['First person neuter plural past pluperfect'] = 'bila smo ' + inflected_word
            self.inflection['Second person neuter plural past pluperfect'] = 'bila ste ' + inflected_word
            self.inflection['Third person neuter plural past pluperfect'] = 'bila su ' + inflected_word
            self.inflection['First person neuter plural conditional I'] = inflected_word + ' bismo'
            self.inflection['Second person neuter plural conditional I'] = inflected_word + ' biste'
            self.inflection['Third person neuter plural conditional I'] = inflected_word + ' bi'
            self.inflection['First person neuter plural conditional II'] = 'bila bismo ' + inflected_word
            self.inflection['Second person neuter plural conditional II'] = 'bila biste ' + inflected_word
            self.inflection['Third person neuter plural conditional II'] = 'bila bi ' + inflected_word
        elif form == 'ppp.ms':
            self.inflection['Passive past participle masculine singular'] = inflected_word
        elif form == 'ppp.fs':
            self.inflection['Passive past participle feminine singular'] = inflected_word
        elif form == 'ppp.ns':
            self.inflection['Passive past participle neuter singular'] = inflected_word
        elif form == 'ppp.mp':
            self.inflection['Passive past participle masculine plural'] = inflected_word
        elif form == 'ppp.fp':
            self.inflection['Passive past participle feminine plural'] = inflected_word
        elif form == 'ppp.np':
            self.inflection['Passive past participle neuter plural'] = inflected_word
        else:
            print('Unknown form: ', form, ' ', inflected_word, ' (', self.word, ' ')

    def _try(self, o): 
        try: 
            return o.__dict__ 
        except: 
            return str(o)

    def toJSON(self):
        return json.dumps(self, default=lambda o: self._try(o), sort_keys=True, indent=0, separators=(',',':')).replace('\n', '')

    def __str__(self):
        return "{0}: {1}".format(self.part_of_speech, self.meanings)


class Inflection:
    
    def __init__(self, word, heading):
        self.word = word
        self.type = heading.title

        match = _inflection_template_regex.search(heading.text)
        if match:
            self.template_name = match.groupdict()['template_name']
            self.template_params = self.parse_template_params(match.groupdict()['params'])
            #TODO: PJC retrieve template from https://en.wiktionary.org/wiki/Template:sh-adj-full?action=raw (sh-adj-full is replaced by self.template_name) and parse it            
            #TODO: PJC template parsing should probably go in parser.py
            self.template = Template.get(self.template_name)
            #TODO: PJC use template to get word forms
        
    
    def parse_template_params(self, params_text):
        template_params = {}
        param_list = params_text.split('|')
        param_num = 1
        for param in param_list:
            if '=' in param:
                named_param = param.split('=')
                template_params[param[0]] = param[1]
            else:
                template_params[str(param_num)] = param
                param_num += 1
        return template_params
