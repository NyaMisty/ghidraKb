import os
import xmltodict
import json

import javakey
JavaKeysMap = {v:k for k,v in javakey.JavaKeys.items()}
JavaModMap = {v:k for k,v in javakey.JavaModifiers.items()}


def getKb(kbxmlFile):
    with open(kbxmlFile, 'rb') as f:
        defaults = xmltodict.parse(f)
    options = {c['@NAME']: c for c in defaults['CATEGORY']['WRAPPED_OPTION']}
    return options

def buildKb(kbdict, baseFile):
    with open(baseFile, 'rb') as f:
        defaults = xmltodict.parse(f)
    kblist = list(sorted(kbdict.values(), key=lambda x: x['@NAME'].split(' ')[::-1]))
    defaults['CATEGORY']['WRAPPED_OPTION'] = kblist
    return xmltodict.unparse(defaults, pretty=True)

def getKbDiff(kbNew, kbDef, opts):
    ret = {}
    kbNew = dict(kbNew)
    kbDef = dict(kbDef)
    for k in opts:
        newDef = kbNew.pop(k, None)
        oldDef = kbDef.pop(k, None)
        if newDef is None:
           continue
        if newDef != oldDef:
            #print('Changed: ', k, oldDef, newDef)
            changed = True
            if oldDef is not None:
                ksold = processKeyStroke(oldDef)
                ksnew = processKeyStroke(newDef)
                if ksnew is not None and ksold is not None:
                    if ksnew.replace('CTRL', 'META') == ksold:
                        # ignore ctrl <-> meta diff
                        changed = False
            if changed:
                ret[k] = newDef
    print("Remaining def: ", list(kbNew), kbDef)
    return ret

def processKeyStroke(ks, short=True):
    if not 'STATE' in ks:
        return None
    vals = {c['@NAME']: int(c['@VALUE']) for c in ks['STATE']}
    k = JavaKeysMap[vals['KeyCode']]
    v = vals['Modifiers']
    mm = []
    for i in range(20):
        m = 1 << i
        if v & m:
            if m not in JavaModMap:
                raise Exception('No javaMod for 1 << %d' % i)
            mk = JavaModMap[m]
            if short:
                if not "_DOWN_" in mk:
                    mm.append(mk)
            else:
                mm.append(mk)
    return '+'.join([*mm, k])

GHIDRA_VERSION = '10.2.3'
OTHER_KBXML_DIR = './other_kbxmls'
DEFAULT_KBXML = './defaults/ghidra_default_%s.kbxml' % GHIDRA_VERSION
KB_KEYS = './defaults/ghidra_default_%s.json' % GHIDRA_VERSION

_, _, kbxmlFiles = next(os.walk(OTHER_KBXML_DIR))
kbxmls = {f: getKb(OTHER_KBXML_DIR + '/' + f) for f in kbxmlFiles}
defaultKb = getKb(DEFAULT_KBXML)
defaultOpts = json.load(open(KB_KEYS))

kbxmlDiffs = {}
for f, kbxml in kbxmls.items():
    print('Processing %s' % f)
    kbxmlDiffs[f] = getKbDiff(kbxml, defaultKb, defaultOpts)
    print('   Diffs:')
    for k in kbxmlDiffs[f].keys():
        print('        ' + k)

kbxmlAllDiff = {}
for frm, diff in kbxmlDiffs.items():
    for k,v in diff.items():
        if not k in kbxmlAllDiff:
            kbxmlAllDiff[k] = {}
        kbxmlAllDiff[k][frm] = v

for action,v in kbxmlAllDiff.items():
    keys = list(set(json.dumps(c) for c in v.values()))
    if len(keys) > 1:
        print('Conflicting: %s' % action)
        v = dict(v)
        v['default'] = defaultKb.get(action, {})
        for frm, k in v.items():
            print('    ', frm, processKeyStroke(k))


def parseConflictFile(f):
    conflictFile = open(f).read()
    conflicts = conflictFile.split('Conflicting: ')
    conflicts = [c.strip() for c in conflicts if c.strip()]
    resolve = {}
    for conf in conflicts:
        confl = conf.splitlines()
        action = confl[0].strip()
        sel = None
        for l in confl:
            l = l.strip()
            if l.startswith('+'):
                sel = l[1:].split(' ')[0]
        resolve[action] = sel

    return resolve

import sys
if len(sys.argv) == 1:
    sys.exit(0)

conflictResolves = parseConflictFile(sys.argv[1])
print('Conflict Resolve: ', conflictResolves)

finalKbxml = dict(defaultKb)
for action, keys in kbxmlAllDiff.items():
    firstK = dict(next(iter(keys.values())))
    #print(action, keys)
    keys_ = list(set(json.dumps(c) for c in keys.values()))
    if len(keys_) == 1:
        finalKbxml[action] = firstK
    else:
        print('Resolving Conflict: ', action)
        resolve = conflictResolves[action]
        if resolve is None:
            finalKbxml[action] = firstK
            finalKbxml[action].pop('STATE')
            finalKbxml[action]['CLEARED_VALUE'] = None
        elif resolve == 'default':
            finalKbxml[action] = dict(defaultKb.get(action))
        else:
            finalKbxml[action] = keys[resolve]

print(buildKb(finalKbxml, DEFAULT_KBXML))
