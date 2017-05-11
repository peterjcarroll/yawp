# from yawp.parser import YAWiktionaryParser

# p = YAWiktionaryParser()
# e = p.get('pivo')
# print(e)

from yawp.dict import serbocroatian

definitions = serbocroatian.get('biti')
for d in definitions:
    print(d.word)
    print(d)
    print(d.inflection)