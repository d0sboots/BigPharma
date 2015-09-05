#!/usr/bin/python

"""Parses effects.data and strings-en.data to produce the table of all cures"""

import collections
import json
import re

# Write dict keys as constants, to protect against typos
ID = 'id'
FAMILY = 'family'
LEVEL = 'level'
BASE_VALUE = 'baseValue'
BOUNDARY = 'boundary'
REACTION = 'reaction'
UPGRADE = 'upgrade'
COMBINE = 'combine'
MACHINE = 'machine'
PRODUCT = 'product'
CONC = 'conc'
CODE = 'code'
TEXT = 'text'

def family_key(family):
  return family + 'title'

# JSON doesn't include C++ style comments in its standard...
comment_pat = re.compile('//.*$', re.MULTILINE)
with open('strings-en.data') as f:
  dat = comment_pat.sub('', f.read()).replace('\t', ' ')
  STRINGS = json.loads(dat)
with open('effects.data') as f:
  dat = comment_pat.sub('', f.read()).replace('\t', ' ')
  EFFECTS = json.loads(dat)

effects_dict = collections.defaultdict(list)

for eff in EFFECTS:
  if eff[LEVEL] < 0:
    continue
  effects_dict[eff[FAMILY]].append(eff)

family_order = effects_dict.keys()
family_order.sort(key=lambda x:(-len(effects_dict[x]),x))

catalysts = dict(("catalyst" + str(x), x + 1) for x in range(1,9))

translations = {}
for string in STRINGS:
  translations[string[CODE]] = string[TEXT]

dat = []
for family in family_order:
  effs = effects_dict[family]
  column = []
  for eff in effs:
    column.append("""{{CureInfo
| Name = %s
| Worth = %d
| Stage = %d
| Range = %d-%d
}}""" % (translations[eff[ID]], eff[BASE_VALUE], eff[LEVEL] + 1,
         eff[BOUNDARY][0], eff[BOUNDARY][1]))
    if REACTION in eff:
      reac = eff[REACTION][UPGRADE]
      column.append('{{UpgradeArrow}}')
      upgrade = '{{CureUpgradeInfo\n'
      if COMBINE in reac:
        upgrade += '| Catalyst = %d\n' % catalysts[reac[COMBINE]]
      upgrade += """| Prerequirement = %d-%d
| Machine = %s
}}""" % (reac[CONC][0], reac[CONC][1], translations[reac[MACHINE]])
      column.append(upgrade)
      column.append('{{UpgradeArrow}}')
  dat.append(column)

print ('<!-- This page was auto-generated using ' +
    'https://github.com/d0sboots/BigPharma/blob/master/pharmascript.py --->')
for i in range(0, len(family_order), 3):
  jend = i + 3
  if jend > len(family_order):
    jend = len(family_order)
  jr = range(i, jend)
  if i != 0:
    print '\n'
  print '<table style="background-color: rgb(148, 148, 148); border: 0px solid grey">'
  print ('<tr style="text-align:center; background-color:#6e6e6e; ' +
         'font-weight:bold; font-size: 20px; color: white; margin-top: 0">')
  for j in jr:
    print '<td style="padding: 10px">%s</td>' % translations[
        family_key(family_order[j])]
  print '</tr>'
  k = 0
  while True:
    seen = False
    for j in jr:
      if k >= len(dat[j]):
        continue
      if not seen:
        print '<tr>'
        seen = True
      print '<td>'
      print dat[j][k]
      print '</td>'
    if seen:
      print '</tr>'
      k += 1
    else:
      break
  print '</table>'
