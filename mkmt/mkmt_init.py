#mkmt refactored version

#Save init version as another file, import it into main. 

import ast
import numpy as np
import operator as op
import requests as rq
from copy import deepcopy
from itertools import chain
from collections import defaultdict

# LINE_JOIN_MODE = "Shell"  # This can be "Shell" or "Django"  # (This is being reworked)
# LINE_JOIN_MODE = ["Shell", "Django"].index(LINE_JOIN_MODE)
CK_LEVEL_LIST = ["NSI", "SSI", "GSI"]
WEIGHTS_DEF = {"Check": np.array([1.0, 1.1, 1.15]), "Counter": np.array([0.02, 0.2, 1])}
COMBO_LIMIT = 12376  #Combinations limit; the maximum number of teams rated in a generation
COMBO_LIMIT_CT = 100947  #Higher combinations limit for counterteaming

#THIS HANDLES MATH IN STRINGS
operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg}

def eval_expr(expr):
    """
    >>> eval_expr('2^6')
    4
    >>> eval_expr('2**6')
    64
    >>> eval_expr('1 + 2*3**(4^5) / (6 + -7)')
    -5.0
    """
    return eval_(ast.parse(expr, mode='eval').body)

def eval_(node):
    if isinstance(node, ast.Num): # <number>
        return node.n
    elif isinstance(node, ast.BinOp): # <left> <operator> <right>
        return operators[type(node.op)](eval_(node.left), eval_(node.right))
    elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
        return operators[type(node.op)](eval_(node.operand))
    else:
        raise TypeError(node)

#Math padder
def zpad(in_, pad_len, str_trunc=True):
    if isinstance(in_, int):
        out0 = "%d" % in_
        out0 = out0[:pad_len]
        out0 = " " * (3-len(out0)) + out0  #pads assuming 3-digit
    elif isinstance(in_, float):
        out0 = "%f" % in_
        out0 = out0[:pad_len]
        out0 = " " * (3 - out0.index(".")) + out0  #pads assuming 3-digit int part
    else:
        out0 = "%s" % in_
        if str_trunc:
            out0 = out0[:pad_len]
    
    return out0 + " " * (pad_len-len(out0))

# --- MKMT INITIALIZATION ---

#New checks compendium: array of all Pokemon where index is Pokemon ID and value is check level
#New way to interpret it: convert check levels to corresponding weights before set of calculations are done


#add a percentage-based system to sus


#First: get checks data and build checks data structure

try:
    with open("checks.txt") as checks_object:  #Loading checks comp
        checks = checks_object.read()
except IOError: 
    checks = rq.get('https://gist.githubusercontent.com/UberPyro/d0e14aaaa8a7e7e472e58f27a9e68778/raw/2d168c387496f9f7ddd95aa5cb31c0db01f00ad3/checks.txt').text

checks = checks.split("\n")  #Taking out the garbage
checks = [i.rstrip(",").split(", ") for i in checks] # Fixed trailing commas
checks = [i for i in checks if len(i) >= 2]
checks = [i for i in checks if i[1] in CK_LEVEL_LIST]

#Deal with all pipes ("|") [this is really messy and bad, I know]
checks = [i[:2] + list(chain.from_iterable([filter(lambda not_trash: not_trash!="|??",   #And this continues onto the next line...
["|".join([(j if "|" in j else j+"|??").split("|")[0], k]) for k in (j if "|" in j else j+"|??").split("|")[1:]]) for j in i[2:]])) for i in checks]
checks = list(chain.from_iterable([[["|".join([(i[0] if "|" in i[0] else i[0]+"|??").split("|")[0], j])]+i[1:] for j in (i[0] if "|" in i[0] else i[0]+"|??").split("|")[1:]] for i in checks]))

#Create aps; aps = All Pokemon Sets
aps_left = list(set(i[0] for i in checks))  #All Pokemon Sets which exist on the left side of the checks compendium
aps_right = filter(lambda not_trash: not_trash!="|??", set(chain.from_iterable(i[2:] for i in checks)))
aps_list_full = list(set().union(aps_left, aps_right))
aps_list = aps_list_full[:]  #subtract exclusions here
aps_dict = {"by":aps_left, "to":aps_right}

#Create a checks dictionary that uses real names (as opposed to an ID)
checkp = deepcopy(checks)  #"physical" checks comp (so its not numbers and it won't contain weights)
checkp = {i:defaultdict(list, {j:k[2:] for j in ["NSI", "SSI", "GSI"] for k in checkp if k[:2]==[i, j]}) for i in aps_left}
checkp2 = {i:{j+" to":[k for k, l in checkp.iteritems() if i in l[j]] for j in ["NSI", "SSI", "GSI"]} for i in aps_right}  #NSI/SSI/GSI To
checkp = {i:dict(checkp.get(i, {}), **checkp2.get(i, {})) for i in aps_list_full}  #Merging dicts

#Encode Pokemon Sets into integers
apsnl = map(aps_list.index, aps_left)
apsnr = map(aps_list.index, aps_right)
apsn = map(aps_list.index, aps_list)
apsnd = {"by":apsnl, "to":apsnr}

apsnlf = map(aps_list_full.index, aps_left)
apsnrf = map(aps_list_full.index, aps_right)
apsnf = map(aps_list_full.index, aps_list)
apsndf = {"by":apsnlf, "to":apsnrf}

checks_array = np.zeros((len(aps_list_full),)*2, dtype=np.int8)
for checks_line in checks:
    ck_level = {"NSI": 1, "SSI": 2, "GSI": 3}[checks_line[1]]
    for cntr in checks_line[2:]:
        checks_array[aps_list_full.index(checks_line[0]), aps_list_full.index(cntr)] = ck_level

checks = {"by": checks_array, "to": checks_array.T}

#To then change the weighting do this: 
#np.hstack((np.zeros(1), WEIGHTS_DEF["Check"]))[checks["to"]]
#(or call apply_weights)

#Second: get usage data and build sus data structure

#GENERATE SET USAGE STATS

try:
    with open("set_link.txt") as link_object:
        link = link_object.read()
except IOError:
    link = rq.get('https://gist.githubusercontent.com/UberPyro/f9cd27f75931b673fc5facbf957e9e37/raw/a01e1b788aacbb593b0c5668438f2f2b34fa36af/set_link.txt').text
set_dict = ast.literal_eval(link)

try:
    with open("usage.txt") as usage_object:
        usage = usage_object.read()
        
    with open("moveset_usage.txt") as set_usage_object:
        set_usage = set_usage_object.read()
    
    usage_origin = "source file"
        
except IOError:
    m0 = 6
    y0 = 17
    m1 = 0
    while rq.get(
    'http://www.smogon.com/stats/20%s-%s/gen7ou-1825.txt' % (
    str((m0+m1) // 12 + y0),
    (lambda x: x if len(x)==2 else "0"+x)(str((m0+m1) % 12))
    )
    ).status_code == rq.codes.ok:
        m1 += 1
    m1 -= 1
    tup = (
    str((m0+m1) // 12 + y0),
    (lambda x: x if len(x)==2 else "0"+x)(str((m0+m1) % 12))
    )
    usage = rq.get('http://www.smogon.com/stats/20%s-%s/gen7ou-1825.txt' % tup).text
    set_usage = rq.get('http://www.smogon.com/stats/20%s-%s/moveset/gen7ou-1825.txt' % tup)
    set_usage.encoding = 'UTF_8'
    set_usage = set_usage.text
    usage_origin = tup

sus_res = "\n%s\n\n" % "".join(map(
zpad,
(" #", "Pokemon Set", "  Combined", "   Pokemon", "   Set"),
(6,    35,            12,         13,        13)
))

aps_no_set = [i.split("|")[0] for i in aps_list_full]

filler = "  "
set_data = []
for i in aps_list_full:
    
    j = i.split("|")[0]
    mon_count = aps_no_set.count(j)
    if mon_count > 1 and i in set_dict:  #if the Pokemon has multiple sets...
    
        k = set_dict[i]
        
        L = ""
        if isinstance(k, tuple):  #if provided a math operation, initialize math operation (new)
            k, L = k
            
        #fet the set-usage-per-Pokemon from a unique identifier in the moveset usage
                                                                                      #First finds pokemon in moveset_usage.txt, then finds set (since it must follow), 
        percent_position = set_usage.find(k,set_usage.find(j + filler))+len(k)+1      #then add length of set name, then add one to account for space
        percent_usage_raw = set_usage[percent_position:percent_position + 6]   #Grabs 5 digit decimal
        set_percent = float(percent_usage_raw.strip(" "))                      #Strips spaces and converts to float
        
        percent_position = usage.find(j + filler) + 21                   #Finds Pokemon in usage.txt, then adds 21 to get to the percent
        percent_usage_raw = usage[percent_position:percent_position + 8] #Grabs 7 diget decimal
        Pokemon_percent = float(percent_usage_raw.strip(" "))            #Strips spaces and converts to float
        
        if L:  #if provided a math operation, execute math operation
            set_percent = eval_expr(L.replace("x", str(set_percent)))
        
        Pokemon_set_percent = round(set_percent * Pokemon_percent / 100.0, 7) #Now we have all ours percentages
        Pokemon_set = i
        
        set_data.append([Pokemon_set, Pokemon_set_percent, Pokemon_percent, set_percent])
    
    elif mon_count == 1:  #else if the Pokemon has only 1 set, assume that set has 100% set-usage-per-Pokemon
        
        percent_position = usage.find(j + filler) + 21                   #Finds Pokemon in usage.txt, then adds 21 to get to the percent
        percent_usage_raw = usage[percent_position:percent_position + 8] #Grabs 7 diget decimal
        Pokemon_percent = float(percent_usage_raw.strip(" "))            #Strips spaces and converts to float
        
        Pokemon_set = i
        
        set_data.append([Pokemon_set, Pokemon_percent, Pokemon_percent, 100.0])
    
percent_position = usage.find("Greninja-Ash"+filler) + 21               #Greninja-Ash (Greninja|ash) hard coding
percent_usage_raw = usage[percent_position:percent_position + 8]        #(This must be removed if Greninja-Ash is removed)
Pokemon_percent = float(percent_usage_raw.strip(" "))                   #^
                                                                        #^
Pokemon_set = "Greninja|ash"                                            #^
                                                                        #^
set_data.append([Pokemon_set, Pokemon_percent, Pokemon_percent, 100.0]) #^

set_data.sort(key = lambda s_sort: s_sort[1], reverse = True)

sus_res += "\n".join([
"".join(map(
zpad,
["[%d]" % j, i[0], i[1], i[2], i[3]],
[6, 35, 12, 13, 13]
))
for j, i in enumerate(set_data, 1)
])

#INTERPRET SET USAGE STATS

sus = deepcopy(sus_res)

sus = filter(None, sus.split("\n")[2:])
sus = [[j.strip(" ") for j in [i[6:39], i[41:52], i[53:62], i[64:70]]] for i in sus]  #Interprets usage_stats_by_set.txt by using indices for strings
sus = [i[:1] + map(float, i[1:]) for i in sus]

sus_dict = {i[0]:i[1]/6 for i in sus}  #Turning into a dictionary because dictionary fast much
sus_dict_full = {i[0]:(i[1], i[2], i[3]) for i in sus}

sum_dict = {i:sum([sus_dict[j] for j in aps_dict[i] if j in sus_dict]) for i in checks}  #Usage sum for each category; /6 since usage stats sum to 600% (6 mons per team)

susn_dict = defaultdict(float, {aps_list_full.index(i):j for i, j in sus_dict.iteritems() if i in aps_list_full})  #Pokemon Set in ID form
sus_array = np.array([susn_dict[i] for i in range(len(aps_list_full))])  #sus in array form

sus_array_blind = np.repeat(1.0, len(aps_list_full))  #alternate unweighted sus_array
# sus_array_blind = np.repeat(100.0 / len(aps_list_full), len(aps_list_full))  # old version

def apply_weights(weights, ck_dir, checks=checks):  #check level and direction (and checks data)
    return np.hstack((np.zeros(1), weights))[checks[ck_dir]]  #WEIGHTS_DEF[ck_lv]  (old code)