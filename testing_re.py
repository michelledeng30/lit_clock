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


text = """
twenty-three minutes past ten blah
twenty-three minutes after ten blah
half past six blah
half past four
quarter past six blah
four minutes to one yeah
four minutes before seven yeah
midnight yeah
noon.
quarter past Midnight.
Midnight
12 o'clock 
eight o'clock 
one o'clock 
4 o'clock
one minute before noon
one to two
"""



# 15

re_onetonineteen = '(?:[Oo]ne|[Tt]wo|[Tt]hree|[Ff]our|[Ff]ive|[Ss]ix|[Ss]even|[Ee]ight|[Nn]ine|[Tt]en|[Ee]leven|[Tt]welve|[Tt]hirteen|[Ff]ourteen|[Ff]ifteen|[Ss]ixteen|[Ss]eventeen|[Ee]ighteen|[Nn]ineteen)'
re_first = '(?:[Qq]uarter|[Hh]alf|[Oo]ne|[Tt]wo|[Tt]hree|[Ff]our|[Ff]ive|[Ss]ix|[Ss]even|[Ee]ight|[Nn]ine|[Tt]en|[Ee]leven|[Tt]welve|[Tt]hirteen|[Ff]ourteen|[Ff]ifteen|[Ss]ixteen|[Ss]eventeen|[Ee]ighteen|[Nn]ineteen)'
re_last = '(?:[Oo]ne|[Tt]wo|[Tt]hree|[Ff]our|[Ff]ive|[Ss]ix|[Ss]even|[Ee]ight|[Nn]ine|[Tt]en|[Ee]leven|[Tt]welve|[Mm]idnight|[Nn]oon)'
regexp1 = '(?:[Tt]wenty|[Tt]hirty|[Ff]orty|[Ff]ifty)' + '[-\s]' + re_onetonineteen + '\s?-?(?:minute\s|minutes\s)?' + '(?:past|after|to|before)\s?' + re_last
regexp2 = re_first + '\s?-?(?:minute\s|minutes\s)' + '(?:past|after|to|before)\s?' + re_last
regexp3 = '(?:[Hh]alf|[Qq]uarter)\s' + '(?:past|after|to|before)\s?' + re_last
regexp4 = '[a-zA-Z0-9]+\so\'clock'
regexp5 = '[Mm]idnight|[Nn]oon'


regexp = regexp1 + '|' + regexp2 + '|' + regexp3 + '|' + regexp4 + '|' + regexp5

result = re.findall(regexp, text)

print(result, len(result))

map_hour = {
    '0': ['0', 'zero', 'Zero', 'midnight', 'Midnight'],
    '1': ['1', 'one', 'One'],
    '2': ['2', 'two', 'Two'],
    '3': ['3', 'three', 'Three'],
    '4': ['4', 'four', 'Four'],
    '5': ['5', 'five', 'Five'],
    '6': ['6', 'six', 'Six'],
    '7': ['7', 'seven', 'Seven'],
    '8': ['8', 'eight', 'Eight'],
    '9': ['9', 'nine', 'Nine'],
    '10': ['10', 'ten', 'Ten'],
    '11': ['11', 'eleven', 'Eleven'],
    '12': ['12', 'twelve', 'Twelve', 'noon', 'Noon']
}

map_minute = {
    '0': ['0', 'zero', 'Zero'],
    '1': ['1', 'one', 'One'],
    '2': ['2', 'two', 'Two'],
    '3': ['3', 'three', 'Three'],
    '4': ['4', 'four', 'Four'],
    '5': ['5', 'five', 'Five'],
    '6': ['6', 'six', 'Six'],
    '7': ['7', 'seven', 'Seven'],
    '8': ['8', 'eight', 'Eight'],
    '9': ['9', 'nine', 'Nine'],
    '10': ['10', 'ten', 'Ten'],
    '11': ['11', 'eleven', 'Eleven'],
    '12': ['12', 'twelve', 'Twelve'],
    '13': ['13', 'thirteen', 'Thirteen'],
    '14': ['14', 'fourteen', 'Fourteen'],
    '15': ['15', 'fifteen', 'Fifteen', 'quarter', 'Quarter'],
    '16': ['16', 'sixteen', 'Sixteen'],
    '17': ['17', 'seventeen', 'Seventeen'],
    '18': ['18', 'eighteen', 'Eighteen'],
    '19': ['19', 'nineteen', 'Nineteen'],
    '20': ['20', 'twenty', 'Twenty'],
    '21': ['21', 'twenty-one', 'Twenty-one'],
    '22': ['22', 'twenty-two', 'Twenty-two'],
    '23': ['23', 'twenty-three', 'Twenty-three'],
    '24': ['24', 'twenty-four', 'Twenty-four'],
    '25': ['25', 'twenty-five', 'Twenty-five'],
    '26': ['26', 'twenty-six', 'Twenty-six'],
    '27': ['27', 'twenty-seven', 'Twenty-seven'],
    '28': ['28', 'twenty-eight', 'Twenty-eight'],
    '29': ['29', 'twenty-nine', 'Twenty-nine'],
    '30': ['30', 'thirty', 'Thirty', 'half', 'Half'],
    '31': ['31', 'thirty-one', 'Thirty-one'],
    '32': ['32', 'thirty-two', 'Thirty-two'],
    '33': ['33', 'thirty-three', 'Thirty-three'],
    '34': ['34', 'thirty-four', 'Thirty-four'],
    '35': ['35', 'thirty-five', 'Thirty-five'],
    '36': ['36', 'thirty-six', 'Thirty-six'],
    '37': ['37', 'thirty-seven', 'Thirty-seven'],
    '38': ['38', 'thirty-eight', 'Thirty-eight'],
    '39': ['39', 'thirty-nine', 'Thirty-nine'],
    '40': ['40', 'forty', 'Forty'],
    '41': ['41', 'forty-one', 'Forty-one'],
    '42': ['42', 'forty-two', 'Forty-two'],
    '43': ['43', 'forty-three', 'Forty-three'],
    '44': ['44', 'forty-four', 'Forty-four'],
    '45': ['45', 'forty-five', 'Forty-five'],
    '46': ['46', 'forty-six', 'Forty-six'],
    '47': ['47', 'forty-seven', 'Forty-seven'],
    '48': ['48', 'forty-eight', 'Forty-eight'],
    '49': ['49', 'forty-nine', 'Forty-nine'],
    '50': ['50', 'fifty', 'Fifty'],
    '51': ['51', 'fifty-one', 'Fifty-one'],
    '52': ['52', 'fifty-two', 'Fifty-two'],
    '53': ['53', 'fifty-three', 'Fifty-three'],
    '54': ['54', 'fifty-four', 'Fifty-four'],
    '55': ['55', 'fifty-five', 'Fifty-five'],
    '56': ['56', 'fifty-six', 'Fifty-six'],
    '57': ['57', 'fifty-seven', 'Fifty-seven'],
    '58': ['58', 'fifty-eight', 'Fifty-eight'],
    '59': ['59', 'fifty-nine', 'Fifty-nine'],
}

def get_key(val, mapping):
    for key in mapping:
        if val in mapping[key]:
            return key
    return -1

def change_format(times):
    converted = []
    for time in times:
        words = time.split()
        if 'o\'clock' in time:
            hour = time.replace(' o\'clock', '')
            hour_key = get_key(hour, map_hour)
            if hour_key == -1:
                print('couldn\'t find ', time, hour)
                return
            converted.append(hour_key + ':00')
        
        
        elif 'past' in words or 'after' in words:
            hour = words[len(words)-1]
            hour_key = get_key(hour, map_hour)
            if hour_key == -1:
                print('couldn\'t find ', time, hour)
                return
            minute = words[0]
            min_key = get_key(minute, map_minute)
            if min_key == -1:
                print('couldn\'t find ', time, minute)
                return
           
            converted.append(hour_key + ':' + min_key)
        
        elif 'to' in words or 'before' in words:
            hour_plusone = words[len(words)-1]
            hour_plusone_key = get_key(hour_plusone, map_hour)
            if hour_plusone_key == -1:
                print('couldn\'t find ', time, hour_plusone)
                return
            hour_key = '12' if hour_plusone_key == '1' else str(int(hour_plusone_key)-1)

            minute = words[0]
            min_opp_key = get_key(minute, map_minute)
            if min_opp_key == -1:
                print('couldn\'t find ', time, minute)
                return
            min_key = str(60 - int(min_opp_key))
            
            converted.append(hour_key + ':' + min_key)
        
        elif len(words) == 1:
            hour_key = get_key(words[0], map_hour)
            converted.append(hour_key + ':00')
        else:
            converted.append('00:00')
            print('did not match', time)

    return converted
                

change_format(result)

