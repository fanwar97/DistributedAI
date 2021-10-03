__author__ = 'zGreg'
import argparse
from datetime import datetime
import numpy as np

def pizd(time,nb):
 """
 Generates nb domains name according to pizd DGA
 :param time: Beginning of the 8' 35" long time interval
 :param nb: Number of domain name to generate, default (as seen in DGA) is 85
 :return: a nb-long list of domain names
 """
 wordlist = ['above',
     'action',
     'advance',
     'afraid',
     'against',
     'airplane',
     'almost',
     'alone',
     'already',
     'although',
     'always',
     'amount',
     'anger',
     'angry',
     'animal',
     'another',
     'answer',
     'appear',
     'apple',
     'around',
     'arrive',
     'article',
     'attempt',
     'banker',
     'basket',
     'battle',
     'beauty',
     'became',
     'because',
     'become',
     'before',
     'begin',
     'behind',
     'being',
     'believe',
     'belong',
     'beside',
     'better',
     'between',
     'beyond',
     'bicycle',
     'board',
     'borrow',
     'bottle',
     'bottom',
     'branch',
     'bread',
     'bridge',
     'bright',
     'bring',
     'broad',
     'broken',
     'brought',
     'brown',
     'building',
     'built',
     'business',
     'butter',
     'captain',
     'carry',
     'catch',
     'caught',
     'century',
     'chair',
     'chance',
     'character',
     'charge',
     'chief',
     'childhood',
     'children',
     'choose',
     'cigarette',
     'circle',
     'class',
     'clean',
     'clear',
     'close',
     'clothes',
     'college',
     'company',
     'complete',
     'condition',
     'consider',
     'contain',
     'continue',
     'control',
     'corner',
     'country',
     'course',
     'cover',
     'crowd',
     'daughter',
     'decide',
     'degree',
     'delight',
     'demand',
     'desire',
     'destroy',
     'device',
     'difference',
     'different',
     'difficult',
     'dinner',
     'direct',
     'discover',
     'distance',
     'distant',
     'divide',
     'doctor',
     'dollar',
     'double',
     'doubt',
     'dress',
     'dried',
     'during',
     'early',
     'eearly',
     'effort',
     'either',
     'electric',
     'electricity',
     'english',
     'enough',
     'enter',
     'escape',
     'evening',
     'every',
     'except',
     'expect',
     'experience',
     'explain',
     'family',
     'famous',
     'fancy',
     'father',
     'fellow',
     'fence',
     'fifteen',
     'fight',
     'figure',
     'finger',
     'finish',
     'flier',
     'flower',
     'follow',
     'foreign',
     'forest',
     'forever',
     'forget',
     'fortieth',
     'forward',
     'found',
     'fresh',
     'friend',
     'further',
     'future',
     'garden',
     'gather',
     'general',
     'gentle',
     'gentleman',
     'glass',
     'glossary',
     'goodbye',
     'govern',
     'guard',
     'happen',
     'health',
     'heard',
     'heart',
     'heaven',
     'heavy',
     'history',
     'honor',
     'however',
     'hunger',
     'husband',
     'include',
     'increase',
     'indeed',
     'industry',
     'inside',
     'instead',
     'journey',
     'kitchen',
     'known',
     'labor',
     'ladder',
     'language',
     'large',
     'laugh',
     'laughter',
     'leader',
     'leave',
     'length',
     'letter',
     'likely',
     'listen',
     'little',
     'machine',
     'manner',
     'market',
     'master',
     'material',
     'matter',
     'mayor',
     'measure',
     'meeting',
     'member',
     'method',
     'middle',
     'might',
     'million',
     'minute',
     'mister',
     'modern',
     'morning',
     'mother',
     'mountain',
     'movement',
     'nation',
     'nature',
     'nearly',
     'necessary',
     'needle',
     'neighbor',
     'neither',
     'niece',
     'night',
     'north',
     'nothing',
     'notice',
     'number',
     'object',
     'oclock',
     'office',
     'often',
     'opinion',
     'order',
     'orderly',
     'outside',
     'paint',
     'partial',
     'party',
     'people',
     'perfect',
     'perhaps',
     'period',
     'person',
     'picture',
     'pleasant',
     'please',
     'pleasure',
     'position',
     'possible',
     'power',
     'prepare',
     'present',
     'president',
     'pretty',
     'probable',
     'probably',
     'problem',
     'produce',
     'promise',
     'proud',
     'public',
     'quarter',
     'question',
     'quiet',
     'rather',
     'ready',
     'realize',
     'reason',
     'receive',
     'record',
     'remember',
     'report',
     'require',
     'result',
     'return',
     'ridden',
     'right',
     'river',
     'round',
     'safety',
     'school',
     'season',
     'separate',
     'service',
     'settle',
     'severa',
     'several',
     'shake',
     'share',
     'shore',
     'short',
     'should',
     'shoulder',
     'shout',
     'silver',
     'simple',
     'single',
     'sister',
     'smell',
     'smoke',
     'soldier',
     'space',
     'speak',
     'special',
     'spent',
     'spread',
     'spring',
     'square',
     'station',
     'still',
     'store',
     'storm',
     'straight',
     'strange',
     'stranger',
     'stream',
     'street',
     'strength',
     'strike',
     'strong',
     'student',
     'subject',
     'succeed',
     'success',
     'sudden',
     'suffer',
     'summer',
     'supply',
     'suppose',
     'surprise',
     'sweet',
     'system',
     'therefore',
     'thick',
     'think',
     'third',
     'those',
     'though',
     'thought',
     'through',
     'thrown',
     'together',
     'toward',
     'trade',
     'train',
     'training',
     'travel',
     'trouble',
     'trust',
     'twelve',
     'twenty',
     'understand',
     'understood',
     'until',
     'valley',
     'value',
     'various',
     'wagon',
     'water',
     'weather',
     'welcome',
     'wheat',
     'whether',
     'while',
     'white',
     'whose',
     'window',
     'winter',
     'within',
     'without',
     'woman',
     'women',
     'wonder',
     'worth',
     'would',
     'write',
     'written',
     'yellow']
 domains = []
 for i in range(0,nb):
  domains.append(generate_domain(bin(time + i), wordlist))
 return domains

def generate_domain(timestamp,wordl):
 """
 Generate one domain name
 :param timestamp: tinm
 :param wordl:
 :return:
 """
 inv_key = [0, 5, 10, 14 ,9 ,3 ,11, 7, 2, 13, 4, 8, 1, 12, 6]
 bin_temp = timestamp[-15::1]
 nib=np.int_(np.zeros(len(bin_temp)))
 for x in range(0,14):
     nib[x] = bin_temp[inv_key[x]]
 res = [''.join([str(char) for char in nib[:7]]),''.join([str(char) for char in nib[7:]])]
 res = [wordl[int(res[0],2)], wordl[int(res[1],2)+128] , ".net" ]
 return ''.join([str(wds) for wds in res])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--date", help="date for which to generate domains")
    parser.add_argument("-n", "--nr", help="nr of domains to generate (default 85)",
           type=int, default=85)
    args = parser.parse_args()

    d = datetime.strptime(args.date, "%Y-%m-%d") if args.date else datetime.now()
    d -= datetime.utcfromtimestamp(0)
    for domain in pizd(int(d.total_seconds()*1000), args.nr):
        print(domain)