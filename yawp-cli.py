# from yawp.parser import YAWiktionaryParser

# p = YAWiktionaryParser()
# e = p.get('pivo')
# print(e)
import sys
from yawp.dict import serbocroatian

definitions = serbocroatian.get(sys.argv[1])
for d in definitions:
    print(d.word)
    print(d)
    print(d.inflection)