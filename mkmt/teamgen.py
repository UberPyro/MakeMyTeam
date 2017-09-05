# from mkmt_init import (
# sus, sus_array, sus_array_blind, sus_dict_full, 
# sum_dict,
# apsnd, apsn, aps_list_full, apsnf, 
# apply_weights, WEIGHTS_DEF,
# zpad,
# COMBO_LIMIT, COMBO_LIMIT_CT,
# checkp, checks,
# )

from django.core.cache import cache
globals().update(cache.get("init"))
# init.update({s: init[s].loads for s in array_keys})

import numpy as np
import operator as op
import itertools as it
from copy import deepcopy


#note for django later: see if form can still exist on page after generating stuff, and if previous enteries could remain autofilled while still on that page. 


# Seperate the initialization (file-reading and processing step) from the rest of the program. This should run at server startup. 
# -> first, change the checks data structure so that the weights are applied lazily. Aditionally, every function must be modified. 

# Refactor every mkmt function as a single function call with an argument list
# -> the previous options menu functions will instead be prompted by every mkmt function, autofilled, and initialized lazily. 

# Use requests for automatic updating during initialization. 
# -> Requests are overrode by correctly named text files in the same directory. 


#APPROACH: LOTS OF FUNCTION DEFINITIONS FOR JOBS SUCH AS GENERATING TEAMS, ETC, NECESSARY FOR THE MKMT FUNCTIONS
#LASTLY, LIST THE MKMT FUNCTIONS


def wformat(sblock):
    return sblock.replace("  ", "&nbsp;&nbsp;").replace("\n", "<br>")

def althigh(sblock):
    bg_color_list = [
    '<span style="background-color:#ffffff;">%s</span>',
    '<span style="background-color:#DFDFDF;">%s</span>'
    ]
    return "\n".join(bg_color_list[i%2] % s for i, s in enumerate(sblock.splitlines()))

def zpad_center(str_to_pad, tot_len):
    n, m = divmod(tot_len - len(str_to_pad), 2)
    return " "*n + str_to_pad + " "*(n + m)

def ncr(n, r):
    r = min(r, n-r)
    if r == 0: return 1
    numer = reduce(op.mul, xrange(n, n-r, -1))
    denom = reduce(op.mul, xrange(1, r+1))
    return numer//denom

def ncr_inv(max_num, sample):  #chooses a pool size such that ncr(pool, sample) < max_num
    if sample == 1: 
        return max_num  #increases speed
    pool = 1
    k = sample
    while pool <= max_num:
        k += 1
        pool = pool * k / (k - sample)
    return k - 1

def rue_idx(a):  #rows-unique-elements index
    idx = a.argsort(1)
    a_sorted = a[np.arange(idx.shape[0])[:,None], idx]
    return (a_sorted[:,1:] != a_sorted[:,:-1]).all(-1)

def get_usage(dmons):  #dmons should already be checked for compatibility with ddir; the starting d means desired
    return (np.clip(dmons.sum(0)-np.arange(dmons.shape[0])[:,None], 0, 1)*sus_array).sum(1)

#def get_checks(dmons, ddir, dweight):
#    return np.clip(dmons.sum(0)-np.arange(dmons.shape[0])[:,None], 0, 1)

dir_dict = {"by":1, "to":-1}
def gen_team(imons, ddir, dweight, genq=6, excl=set(), sus_array=sus_array, checks=checks):
    emons = np.copy(imons)  #Numpy arrays in function arguments are apparently pointed to rather than copied. 
    if genq == 1:
        return gen_team_brute(emons, ddir, dweight, 1, excl)
    ebool = emons.size>0
    cdict = apply_weights(dweight, ddir, checks)
    tpool = np.array(list(set(apsnd[ddir]).difference(imons, excl)))  #tpool (total pool) is an array of all Pokemon which the generator can choose
    tpool = tpool[np.argsort((cdict[tpool]*sus_array).sum(1))[::dir_dict[ddir]]][:160]  #This takes the top 160 Pokemon to make calculations less expensive
    tpool.shape = (1,) + tpool.shape                           #add a gcm sort to it if ram is an issue
    cpool = cdict[tpool]     #counter pool  (fancy indexing here)
    ecount = cdict[emons] if ebool else np.array([])
    emons.shape = emons.shape + (1,)
    
    idx0 = np.argsort((cpool[0]*sus_array).sum(1), axis = 0)[::dir_dict[ddir]]  # do #1 first
    cpool = cpool[:,idx0]
    tpool = tpool[:,idx0].reshape(tpool.shape + (1,))
    tsize = tpool[0].size
    esize = emons.size
    tpool = np.dstack((np.tile(emons, (tsize, 1)).reshape(1, tsize, esize), tpool)) if ebool else tpool
    cpool = (ecount.sum(0) + cpool) if ebool else cpool
    
    idx5 = np.unique(np.sort(np.dstack(np.meshgrid(*[np.array(range(0, tsize))]*2)).reshape(-1, 2), axis=1), axis=0).T
    
    #idx1=Pokemon Sets, idx2=Scores, idx3=Sort Index, idx4=Counter Data, idx5=Product Index, idx6=Unique Index
    for i in range(2, genq + 1):  #Repeat for generation size (UberPyro's Ultimate Loop of Recursive Corebuilding [UULRC])
        q = i                                                                                                    #I think that's what I'm going to call the teambuilding algorithm now.
        i, j = divmod(i, 2)
        k = np.array([i - 1, i + j - 1])
        
        idx2 = np.copy(idx5)  #copy product index            code in this block should probably be broken up so that people other than me can understand it
        idx1 = np.hstack(((np.tile(emons, (idx2.shape[1], 1)).reshape(idx2.shape[1], esize),) if ebool else tuple()) + (tpool[k][0][:, emons.size:][idx2[0]], tpool[k][1][:, emons.size:][idx2[1]]))  #form Pokemon sets
        idx1 = idx1[:, ~np.all(idx1 == 0, axis=0)]  #remove zero columns            ^could probably be done more effectively with np.insert?
        idx4 = (ecount.sum(0) if ebool else 0) + cpool[k][0][idx2[0]] + cpool[k][1][idx2[1]] - (ecount.sum(0)*esize if ebool else 0)  #form counters
        idx6 = rue_idx(idx1)  #remove rows (core combinations) containing duplicate elements                       #(compensate since each cpool array already contains ecount)
        idx7 = np.unique(np.sort(idx1[idx6], axis=1), axis=0, return_index=True)[1]  #removed identical but rearranged rows
        idx1 = idx1[idx6][idx7]  #apply previously defined indexes to Pokemon sets list
        idx4 = idx4[idx6][idx7]  #apply previously defined indexes to Counter data list (these are all parallel arrays)
        idx2 = (np.clip(idx4.reshape(idx4.shape[0], 1, idx4.shape[1]) - np.arange(q+esize)[:,None], 0, 1)*sus_array).sum(2).T  #score Counter data list
        idx3 = np.lexsort(idx2[::dir_dict[ddir]])[::dir_dict[ddir]]  #sort scores list; apply the indexes that sort by score below
        idx2 = idx2.T[idx3][:tsize]  #Scores
        idx1 = idx1  [idx3][:tsize]  #Pokemon Sets
        idx4 = idx4  [idx3][:tsize]  #Data
        
        tpool = np.dstack((tpool, np.zeros(tpool.shape[:-1]+(1,), dtype=np.int)))  #Give tpool an extra array of 0s so everything can have the same dimensions
        tpool = np.vstack((tpool, idx1.reshape((1,)+idx1.shape)))  #Add Pokemon Sets/Cores to tpool
        cpool = np.vstack((cpool, idx4.reshape((1,)+idx4.shape)))  #Add Counter Data       to cpool (this allows for the recursive nature of the algorithm.)
    
    return idx1, idx2

def gen_team_brute(emons, ddir, dweight, genq=1, excl=set(), sus_array=sus_array, checks=checks):  #This function generates and scores all combinations of *top* Pokemon
    #genq = 1 calls will redirect here since they break the main algorithm
    poolq = ncr_inv(COMBO_LIMIT, genq)  #This controls the total number of combinations which can be produced
    tpool = np.array(list(set(apsnd[ddir]).difference(emons, excl)))  #tpool (total pool) is an array of all Pokemon which the generator can choose
    cdict, esize = apply_weights(dweight, ddir, checks), emons.size  # tsize = tpool.size  # not needed any more
    tpool = tpool[np.argsort((cdict[tpool]*sus_array).sum(1))[::dir_dict[ddir]]][:poolq]  #In some cases we may want to reduce the number of Pokemon which the generator uses
    t_mcr = tpool[np.fromiter(it.chain.from_iterable(it.combinations(range(tpool.shape[0]), genq)), int, count=ncr(tpool.shape[0], genq)*genq).reshape(-1, genq)]
    t_mcr = np.hstack((np.tile(emons, (t_mcr.shape[0], 1)).reshape(t_mcr.shape[0], esize), t_mcr)) if esize != 0 else t_mcr
    c_mcr = cdict[t_mcr]  #Fancy indexing to convert pokemon to countersarray
    c_mcr = np.clip(c_mcr.sum(1)[:,None]-np.arange(genq+esize)[:,None], 0, 1)
    c_mcr *= sus_array  # having this with *= makes it much more memory efficient
    c_mcr = c_mcr.sum(2)
    idx = np.lexsort(c_mcr.T[::dir_dict[ddir]])[::dir_dict[ddir]]
    return t_mcr[idx][:200], c_mcr[idx][:200]

def mmsfilt(team_data):  # multiple mega and species filter; also now filters z-moves
    return tuple(team_data[part][idx] for idx in (np.array([team_idx
    for team_idx in xrange(team_data[0].shape[0])
    for team in ([aps_list_full[monID] for monID in team_data[0][team_idx].tolist()],)
    for pkmn_spcs in ([pkmn.split("|")[0] for pkmn in team],)
    if (
    len(pkmn_spcs) == len(set(pkmn_spcs)) and
    len(filter(lambda pkmn: "-Mega" in pkmn, pkmn_spcs)) <= 1 and
    len(filter(lambda pkmn: "z-" in pkmn or "Z DD" in pkmn, team)) <= 1
    )
    ]),)
    for part in xrange(2))

def disp_team(team_data, list_qty):  # remove "/n".join() and apply color alternations when ready
    return "\n\n".join([
    "[%d]%s%s\n      %s" % (
    team_idx + 1,  # team ranking (also its index)
    " " * (4 - len(str(team_idx+1))),  # padding for index
    ", ".join([aps_list_full[pkmn] for pkmn in team_data[0][team_idx].tolist()]),  # convert team from numbers
    "[%s]" % ", ".join(["%g" % percent for percent in team_data[1][team_idx].tolist()]),  # format team score
    )
    for team_idx in xrange(min(team_data[0].shape[0], list_qty))
    ])

def disp_partners(team_data, list_qty):
    return "\n\n".join([
    "[%d]%s%s\n      %s" % (
    team_idx + 1,  # team ranking (also its index)
    " " * (4 - len(str(team_idx+1))),  # padding for index
    aps_list_full[team_data[0][team_idx].tolist()[1]],  # index and output partner
    "[%s]" % ", ".join(["%g" % percent for percent in team_data[1][team_idx].tolist()]),  # format team score
    )
    for team_idx in xrange(min(team_data[0].shape[0], list_qty))
    ])

def disp_suggestions(team_data, list_qty):
    return "\n\n".join([
    "[%d]%s%s\n      %s\n      %s" % (
    team_idx + 1,  # team ranking (also its index)
    " " * (4 - len(str(team_idx+1))),  # padding for index
    "Replace %s with %s." % (  # explain replacement suggestion
    aps_list_full[team_data[2].tolist()[team_idx]],
    aps_list_full[team_data[0][team_idx].tolist()[-1]]
    ),
    ", ".join([aps_list_full[pkmn] for pkmn in team_data[0][team_idx].tolist()]),  # convert team from numbers
    "[%s]" % ", ".join(["%g" % percent for percent in team_data[1][team_idx].tolist()]),  # format team score
    )
    for team_idx in xrange(min(team_data[0].shape[0], list_qty))
    ])

# SEE custom_generator TO SEE HOW INPUTS ARE (generally) HANDLED


def brmt(pkmn_in, ck_weight, cntr_weight, ck_dir, blind):
    
    sus_array = np.copy(globals()["sus_array_blind"] if blind else globals()["sus_array"])
    
    content_data = ""
    weights = {"Check": ck_weight, "Counter": cntr_weight}
    
    for i, m in ((get_usage(apply_weights(weights[l], ck_dir)[pkmn_in]).tolist(), l) for l in ["Check", "Counter"]):
        for k, j in enumerate(i, 1):
            k = 1 + pkmn_in.size - k if ck_dir == "to" else k
            content_data += "%d team member(s) %s %f%% of the metagame, out of %f%% of the metagame available.\n" % (
            k,
            {
            ("Check", "by"): "[Are Checked By]",
            ("Counter", "by"): "[Are Countered By]",
            ("Check", "to"): "[Are Checks To]",
            ("Counter", "to"): "[Are Counters To]"
            }[(m, ck_dir)],
            j,
            sum_dict[ck_dir]
            )
        content_data += "\n"
    
    for m in ["Check", "Counter"]:
        l = apply_weights(weights[m], ck_dir)[pkmn_in].sum(0)
        l = zip(l.tolist(), (l*sus_array).tolist())  # checks, usage-weighted-checks
        content_data += ("List of opposing Pokemon and how many team members %s them.\n"
        "Note that a non-integer indicates a partial coverage.\n"
        "The 'Danger Score' is simply the raw quantity usage-weighted\n"
        "More threatening Pokemon are at the top.\n"
        "\n%s%s%s%s%s%s\n"
        "\n%s\n\n") % (  #gigantic tuple
        {
        ("Check", "by"): "[Are Checked By]",
        ("Counter", "by"): "[Are Countered By]",
        ("Check", "to"): "[Are Checks To]",
        ("Counter", "to"): "[Are Counters To]"
        }[(m, ck_dir)],
        " " * 6,
        "Opposing Pokemon",
        " " * 18,
        "Danger Score",
        " " * 2,
        "Raw Quantity",
        "\n".join([
        "[%d]%s%s%s%f%s%f" % (
        f,
        " " * (4 - len(str(f))),
        g,
        " " * (37 - len(g) - len(str(int(round(h, 6))))),  #35 spaces for mon, 2 for int part of number
        round(h, 6),
        " " * (8 - len(str(int(round(h, 6)))) - len(str(int(round(p, 6))))),
        round(p, 6)
        )
        for f, (g, h, p) in enumerate(sorted(
        ((aps_list_full[k], r, n) for k, (n, r) in enumerate(l) if k in apsnd[ck_dir]),  # monID, (checks, usage-weighed-checks)
        key = lambda brmtsort: brmtsort[1],
        reverse = False if ck_dir == "to" else True
        ), 1)
        ])
        )
    return wformat(althigh(content_data))

def generate_mcr(ck_weight, cntr_weight, ck_dir, ck_lv, blind):
    
    sus_array = np.copy(globals()["sus_array_blind"] if blind else globals()["sus_array"])
    
    aps_array = np.array(apsnf)
    cdict_ = [(apply_weights({"Check": ck_weight, "Counter": cntr_weight}[j], i) * sus_array).sum(1)
              for i in ["to", "by"] for j in ["Check", "Counter"]]
    
    if ck_dir == "by":
        for i in range(len(cdict_)):
            cdict_[i][cdict_[i] == 0.0] = 100
    
    idx = ["to", "by"].index(ck_dir) * 2 + ["Check", "Counter"].index(ck_lv)
    idx = np.argsort(cdict_[idx])[::dir_dict[ck_dir]]
    
    mcr_list = zip(aps_array[idx].tolist(), *[i[idx].tolist() for i in cdict_])
    
    return wformat(althigh("""
Metagame available for [to] data: %f%%
Metagame available for [by] data: %f%%

ck = check, ct = counter
The numbers in the columns are in terms of '%% metagame'

%s%s%s%s%s%s%s%s%s%s%s

%s
""" % (
    sum_dict["to"],
    sum_dict["by"],
    "Rank",
    " " * 2,
    "Pokemon Set",
    " " * 25,
    "ck to",
    " " * 8,
    "ct to",
    " " * 8,
    "ck by",
    " " * 8,
    "ct by",
    
    "\n".join(["[%d]%s%s%s%f%s%f%s%f%s%f" % (
    i,
    " " * (4 - len(str(i))),
    aps_list_full[j],
    " " * (38 - len(aps_list_full[j]) - len(str(int(round(k, 6))))),
    round(k, 6),
    " " * (6 - len(str(int(round(l, 6))))),
    round(l, 6),
    " " * (6 - len(str(int(round(m, 6))))),
    round(m, 6),
    " " * (6 - len(str(int(round(n, 6))))),
    round(n, 6)
    ) for i, (j, k, l, m, n) in enumerate(mcr_list, 1)])
    )))

def pkmn_cov_data(pkmn_in):
    
    return wformat("""
%s

<span style="white-space: normal;">%s</span>

%s

%s

%s
""" % (
    "Pokemon Set: %s" % aps_list_full[pkmn_in.sum()],
    "\n\n".join([
    "%s: %s" % (
    i,
    ", ".join(checkp[aps_list_full[(pkmn_in.tolist()[0])]].get(i, ("{None}",)))
    )
    for i in ["GSI", "SSI", "NSI", "GSI to", "SSI to", "NSI to"]
    ]),
    "\n".join([
    "%s: %s%% of the metagame, out of %s%% available" % (
    {
    ("Check", "to"): "Is A Check To",
    ("Counter", "to"): "Is A Counter To",
    ("Check", "by"): "Is Checked By",
    ("Counter", "by"): "Is Countered By"
    }[(j, i)],
    round((apply_weights(WEIGHTS_DEF[j], i)[pkmn_in] * sus_array).sum(), 4),
    round(sum_dict[i], 4)
    )
    for i in ["to", "by"] for j in ["Check", "Counter"]
    ]),
    "Has NSI/SSI/GSI Data: %s\nHas NSI/SSI/GSI to Data: %s" % (
    pkmn_in.sum() in apsnd["by"],
    pkmn_in.sum() in apsnd["to"]
    ),
    "\n".join([
    "%s: %s%%" % i
    for i in zip(
    ["Pokemon Set Usage", "Pokemon Usage", "Set Usage On Pokemon"],
    sus_dict_full.get(aps_list_full[pkmn_in.sum()], ["NaN"]*3)
    )
    ])
    ))

def partner_finder(pkmn_in, weights, ck_dir, bl_wl, bl_wl_mode, blind, f):
    return custom_generator(pkmn_in, weights, ck_dir, 1, 25, 0, bl_wl, bl_wl_mode, blind, f, disp_partners)

def core_builder(weights, ck_dir, gen_qty, bl_wl, bl_wl_mode, blind, f):
    return custom_generator(np.array([]), weights, ck_dir, gen_qty, 25, 0, bl_wl, bl_wl_mode, blind, f)

def team_generator(weights, ck_dir, bl_wl):
    return custom_generator(np.array([]), weights, ck_dir, 6, 50, 1, bl_wl, 0, False, True)

def team_completer(pkmn_in, weights, ck_dir, bl_wl, bl_wl_mode, blind, f):
    return custom_generator(pkmn_in, weights, ck_dir, 6 - pkmn_in.size, 25, 0, bl_wl, bl_wl_mode, blind, f)

def replacement_suggestor(pkmn_in, weights, ck_dir, bl_wl, bl_wl_mode, blind, f):
    
    if bl_wl_mode:  # False = blacklist, True = whitelist
        bl_wl = np.difference(apsn, bl_wl)
    
    sus_array = np.copy(globals()["sus_array_blind"] if blind else globals()["sus_array"])
    
    f = mmsfilt if f else lambda x: x
    
    mega_list = tuple(  # generate modified teams
    f(gen_team_brute(
    np.setdiff1d(pkmn_in, pkmn_in[i:i+1]), ck_dir, weights, 1, bl_wl, sus_array
    )) + (pkmn_in[i:i+1],)
    for i in xrange(pkmn_in.size)
    )
    
    mega_list = (  # combine teams in seperate lists
    np.vstack(tuple(i[0] for i in mega_list)),
    np.vstack(tuple(i[1] for i in mega_list)),
    np.hstack(tuple(np.repeat(i[2], i[0].shape[0]) for i in mega_list))
    )
    
    idx_ = np.lexsort(mega_list[1].T[::dir_dict[ck_dir]])[::dir_dict[ck_dir]]  # sort suggestions (copied from gen team brute)
    mega_list = tuple(i[idx_] for i in mega_list)  # apply indirect index
    
    return wformat(disp_suggestions(mega_list, 25))

def custom_generator(pkmn_in, weights, ck_dir, gen_qty, list_qty, alg, bl_wl, bl_wl_mode, blind, f, disp_team=disp_team, checks=checks):  # also handles functions which are a specific case of this one
    """
pkmn_in = starting Pokemon / Pokemon that must be in the generation
weights = checks weightings. Choices are given of checking and countering, but custom is available. 
ck_dir = direction of optimization. 'By' or 'to'. Maximize what you check or minimize what checks you. 
gen_qty = quanitity of Pokemon to generate
list_qty = quantity of Pokemon to display
alg = algorithm to use (recursive or top combinations)
bl_wl = Blacklist / Whitelist for excluding Pokemon able to be chosen by the generator
bl_wl_mode = Choosing Blacklist or Whitelist
"""
    if bl_wl_mode:  # False = blacklist, True = whitelist
        bl_wl = np.setdiff1d(apsn, bl_wl)
    
    sus_array_in = np.copy(sus_array_blind if blind else sus_array)
    
    f = mmsfilt if f else lambda x: x
    
    gen_alg = [gen_team_brute, gen_team][alg]  # 0 or 1 to choose algorithm. 0 = Top Combinations, 1 = Recursive. 
    return wformat(disp_team(f(gen_alg(pkmn_in, ck_dir, weights, gen_qty, bl_wl, sus_array_in, checks)), list_qty))  # Just display function. Menu-y stuff will be dealt with later. 

def counterteam_generator(pkmn_in, enmy_in, ck_dir, weights, gen_qty, bl_wl, bl_wl_mode, f):
    
    checks = {k: np.copy(v) for k, v in globals()["checks"].iteritems()}
    
    by_, to_ = np.copy(checks["by"]), np.copy(checks["to"])
    by_[:,np.setdiff1d(np.arange(len(aps_list_full)), enmy_in)] = 0
    to_[:,np.setdiff1d(np.arange(len(aps_list_full)), enmy_in)] = 0
    checks = {"by": by_, "to": to_}
    
    apply_weights = lambda weights_, ck_dir_: np.hstack((np.zeros(1), weights_))[checks[ck_dir_]]
    
    return wformat(custom_generator(pkmn_in, weights, ck_dir, gen_qty, 25, 0, bl_wl, bl_wl_mode, True, f, disp_team, checks))

def team_comparer(teams_in, ck_dir, weights):
    
    largest_team_size = max([o.size for o in teams_in])
    if largest_team_size <= 2:
        largest_team_size = 2
    
    pstr = [("  usage", " (weight)"),("Pokemon Set",)]  # pstr = string to print
    pstr += sum(([(" ",), tuple(aps_list_full[j] for j in i.tolist()), ("",)] for i in teams_in), [])
    
    pstr = [i + (" ",)*(largest_team_size-len(i)) for i in pstr]  #Make all lists the same length
    pstr = zip(*pstr)  #each sub list is now for a different newline
    pstr.append((" ",) * (2+len(teams_in)*3))  #space between pstr and data
    
    c_data = np.vstack((
    sus_array, 
    np.arange(len(aps_list_full))
    ) + tuple(it.chain.from_iterable(
    (
    np.zeros(len(aps_list_full)),
    apply_weights(weights, ck_dir)[i].sum(0),
    np.zeros(len(aps_list_full)),
    )
    for i in teams_in
    ))
    ).T.tolist()
    
    for i in xrange(len(aps_list_full)):
        c_data[i][1] = aps_list_full[int(c_data[i][1])]  #monID --> mon name
        
        if len(teams_in) > 1:  #Win markers
            ext = max if ck_dir == "to" else min
            
            cov0 = c_data[i][3::3]  #maybe put this in an if block to ignore if 1-team
            idx_0 = cov0.index(ext(cov0))
            cov1 = cov0[:idx_0] + cov0[idx_0+1:]
            idx_1 = cov1.index(ext(cov1))
            
            gtr_eql = op.ge if ck_dir == "to" else op.le
            gtr = op.gt if ck_dir == "to" else op.lt
            
            if gtr_eql(cov0[idx_0], 1) and gtr(1, cov1[idx_1]):
                c_data[i][idx_0*3+2] = 2  #have to do *2+2 instead of [2::2] because of extended slice assigning limitations
                c_data[i][idx_0*3+4] = 2
            elif gtr(cov0[idx_0], cov1[idx_1]):
                c_data[i][idx_0*3+2] = 1
                c_data[i][idx_0*3+4] = 1
        
        for j in xrange(2, len(teams_in)*3+2, 3):
            c_data[i][j] = {0: '', 1: '<span style="color:#9400D3;">', 2: '<span style="color:#ff0000;">'}[int(c_data[i][j])]
            c_data[i][j+2] = {0: '', 1:'</span>', 2: '</span>'}[int(c_data[i][j+2])]
    
    
    pstr += c_data
    pstr = [map(zpad, i, [12, 35] + [0, 37, 0]*len(teams_in), [False]*(2+len(teams_in))) for i in pstr]  #all strings are now zero padded to the right
    return wformat(althigh("\n".join(["".join(i) for i in pstr])))

def check_map(pkmn_in_0, pkmn_in_1):

    cgrid = [
    [
    n
    for i in (aps_list_full[p] for p in pkmn_in_1.tolist())
    for n, m in it.chain(checkp[j].iteritems(), (("None", set(aps_list_full).difference(sum(checkp[j].itervalues(),[]))),)) if i in m
    ]
    for j in (aps_list_full[o] for o in pkmn_in_0.tolist())
    ]
    
    cgrid = [[" "*4] + [aps_list_full[p][:17] for p in pkmn_in_0.tolist()]] + [
    [i] + j for i, j in
    it.izip([aps_list_full[o][:17] for o in pkmn_in_1.tolist()], cgrid)
    ]
    
    cgrid = [[zpad_center(i, 17) for i in j] for j in cgrid]
    
    for i in xrange(len(cgrid)):  # Color
        for j in xrange(len(cgrid[i])):
            cgrid[i][j] = {
            "       NSI       ": '<span style="color:#CCCC00;">       NSI       </span>',
            "       SSI       ": '<span style="color:#FF8C00;">       SSI       </span>',
            "       GSI       ": '<span style="color:#ff0000;">       GSI       </span>',
            "     NSI to      ": '<span style="color:#008000;">     NSI to      </span>',
            "     SSI to      ": '<span style="color:#0000ff;">     SSI to      </span>',
            "     GSI to      ": '<span style="color:#800080;">     GSI to      </span>',
            "      None       ": '<span style="color:#808080;">      None       </span>'
            }.get(*(cgrid[i][j],)*2)
    
    cgrid = "\n".join(["    ".join(i) for i in cgrid])
    
    return wformat(cgrid)



# tests of each function

# print brmt(np.array([0, 1, 2, 3, 4, 5]), np.array([1.0, 1.2, 1.3]), np.array([.02, .2, 1]), "by", True)
# print generate_mcr(np.array([1.0, 1.2, 1.3]), np.array([.02, .2, 1]), "to", "Counter", False)
# print pkmn_cov_data(np.array([0]))
# print partner_finder(np.array([0]), np.array([1.0, 1.2, 1.3]), "to", np.array([]), 0, False)
# print core_builder(np.array([1.0, 1.2, 1.3]), "to", 3, np.array([]), 0, False)
# print team_generator(np.array([1.0, 1.2, 1.3]), "to", np.array([]))
# print team_completer(np.array([0]), np.array([1.0, 1.2, 1.3]), "to", np.array([]), 0, False)
# print replacement_suggestor(np.array([0, 1, 2, 3, 4, 5]), np.array([1.0, 1.2, 1.3]), "to", np.array([]), 0, False)
# print custom_generator(np.array([0]), np.array([1.0, 1.2, 1.3]), "to", 3, 25, 0, np.array([]), 0, False)
# print counterteam_generator(np.array([]), np.array([18]), "to", np.array([.02, .2, 1]), 6, np.array([]), 0)
# print team_comparer([np.array([1, 2]), np.array([3, 4]), np.array([5, 6])], "to", np.array([.02, .2, 1]), False)
# print check_map(np.array([0, 1, 2]), np.array([3, 4, 5]))
