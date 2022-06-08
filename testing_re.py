import re

text = """REGAN, MEANWHILE, had begun the exact same day by shooting upright in bed.
SCENE: A lavish master bedroom. Shoes have been mislaid. Articles of clothing have been
flung. Whatever has happened here, no mother would approve.
ACTION: Regan squints at the clock, which reads an abysmal 2:21 P.M.
“Well, fuck me entirely,” Regan announced to the room. 12:31 am ejvdirvfd 1:09"""

# regexp = re.compile("(24:00|2[0-3]:[0-5][0-9]|[0-1][0-9]:[0-5][0-9])")
# result = re.findall(regexp, text)

# print(result)
regexp12 = '1[0-9]:[0-5][0-9]\s?[AaPp]\.?[Mm]\.?|[1-9]:[0-5][0-9]\s?[AaPp]\.?[Mm]\.?'
regexp24 = '24:00|2[0-3]:[0-5][0-9]|1[0-9]:[0-5][0-9]|[0-9]:[0-5][0-9]'

regexp = re.compile(regexp12+'|'+regexp24)
# regexp = re.compile('(1[012]:[0-5][0-9])\s?')
result = re.findall(regexp, text)
print(result)
