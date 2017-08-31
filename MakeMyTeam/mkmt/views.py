# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache

from .forms import (brmtForm, mcrForm, pkmnDataForm, 
                    customForm, partnerForm, coreForm, 
                    genForm, completeForm, replaceForm,
                    counterForm, compareForm, mapForm)
import teamgen as tg

import numpy as np
from ast import literal_eval as le

globals().update({k: v for k, v in cache.get("init").iteritems() if k in [
"aps_list_full", "WEIGHTS_DEF", "sus_res", "usage_origin"
]})

# we're going to need one of these variables for every starting number ( = 1, = 0, etc.)

# A LOT OF WORK TO BE DONE WITH THE FORM

@csrf_exempt
def break_my_team(request):
    
    init_def = {"ck_weight": WEIGHTS_DEF["Check"].tolist(), "cntr_weight": WEIGHTS_DEF["Counter"].tolist()}
    
    global aps_list_full
    
    if request.method == 'POST':
        
        pc = 0
        while "pkmn%d" % pc in request.POST:
            pc += 1
        
        if "calculate" in request.POST:
            
            form = brmtForm(pc)(request.POST)
            if form.is_valid():
                res = render(request, 'contentout.html', {'content':
                tg.brmt(
                np.array([aps_list_full.index(form.cleaned_data['pkmn%d' % i]) for i in xrange(pc)]),
                np.array(le(form.cleaned_data["ck_weight"])),
                np.array(le(form.cleaned_data["cntr_weight"])),
                form.cleaned_data["ck_dir"],
                form.cleaned_data["blind"]
                )
                })
                return res
        
        else:
            
            form = brmtForm(pc)(request.POST)
            reqdata = dict(init_def)
            for i in xrange(pc):
                cont = 'pkmn%d' % i
                if cont in form.data:
                    reqdata.update({cont: form.data[cont]})
            
            if "add_pkmn_field" in request.POST:
                pc += 1
            
            form = brmtForm(pc, False)(initial=reqdata)
    
    else:
        
        form = brmtForm(1, False)(initial=init_def)
        
    return render(request, 'brmtcontent.html', {'form': form})

@csrf_exempt
def mcr_generator(request):
    
    init_def = {"ck_weight": WEIGHTS_DEF["Check"].tolist(), "cntr_weight": WEIGHTS_DEF["Counter"].tolist()}
    
    if request.method == 'POST':
            
        form = mcrForm(request.POST)
        if form.is_valid():
            return render(request, 'contentout.html', {'content':
            tg.generate_mcr(
            np.array(le(form.cleaned_data["ck_weight"])),
            np.array(le(form.cleaned_data["cntr_weight"])),
            form.cleaned_data["ck_dir"],
            form.cleaned_data["ck_lv"],
            form.cleaned_data["blind"]
            )
            })
    
    else:
        
        form = mcrForm(initial=init_def)
        
    return render(request, 'mcrcontent.html', {'form': form})

@csrf_exempt
def Pokemon_data(request):
    
    if request.method == 'POST':
            
        form = pkmnDataForm(request.POST)
        if form.is_valid():
            return render(request, 'contentout.html', {'content':
            tg.pkmn_cov_data(
            np.array([aps_list_full.index(form.cleaned_data["pkmn"])])
            )
            })
    
    else:
        
        form = pkmnDataForm()
        
    return render(request, 'pkmndatacontent.html', {'form': form})

@csrf_exempt
def partner_finder(request):
    
    init_def = {
    # "weights": str(WEIGHTS_DEF["Check"].tolist()) + " # Check Weights (Offense)",
    "bl_rain": True,
    "f": True
    }
    
    global aps_list_full
    
    if request.method == 'POST':
    
        bc = 0
        while "blwl%d" % bc in request.POST:
            bc += 1
        
        if "calculate" in request.POST:
            
            form = partnerForm(bc)(request.POST)
            if form.is_valid():
                res = render(request, 'contentout.html', {'content':
                tg.partner_finder(
                np.array([aps_list_full.index(form.cleaned_data["pkmn"])]),
                np.array(le(form.cleaned_data["weights"])),
                form.cleaned_data["ck_dir"],
                np.union1d(np.array(
                    [aps_list_full.index(form.cleaned_data['blwl%d' % i]) for i in xrange(bc) if form.cleaned_data['blwl%d' % i] in aps_list_full]
                    ), np.array([aps_list_full.index(i) for i in 'Kingdra|??', 'Kabutops|??', 'Omastar|shell smash', 'Swampert-Mega|??'
                                 if form.cleaned_data["bl_rain"] and not int(form.cleaned_data["bl_wl_mode"])])),
                int(form.cleaned_data["bl_wl_mode"]),
                form.cleaned_data["blind"],
                form.cleaned_data["f"]
                )
                })
                return res
        
        else:
            
            form = partnerForm(bc)(request.POST)
            reqdata = dict(init_def)
            for i in xrange(bc):
                cont = 'blwl%d' % i
                if cont in form.data:
                    reqdata.update({cont: form.data[cont]})
            for i in ["pkmn", "weights", "ck_dir", "bl_wl_mode", "blind"]:
                if i in form.data:
                    reqdata.update({i: form.data[i]})
            
            if "add_blwl_field" in request.POST:
                bc += 1
            
            form = partnerForm(bc, False)(initial=reqdata)
    
    else:
        
        form = partnerForm(0, False)(initial=init_def)
        
    return render(request, 'partnercontent.html', {'form': form})

@csrf_exempt
def core_builder(request):
    
    init_def = {
    # "weights": str(WEIGHTS_DEF["Check"].tolist()) + " # Check Weights (Offense)",
    "bl_rain": True,
    "f": True
    }
    
    global aps_list_full
    
    if request.method == 'POST':
    
        bc = 0
        while "blwl%d" % bc in request.POST:
            bc += 1
        
        if "calculate" in request.POST:
            
            form = coreForm(bc)(request.POST)
            if form.is_valid():
                res = render(request, 'contentout.html', {'content':
                tg.core_builder(
                np.array(le(form.cleaned_data["weights"])),
                form.cleaned_data["ck_dir"],
                form.cleaned_data["gen_qty"],
                np.union1d(np.array(
                    [aps_list_full.index(form.cleaned_data['blwl%d' % i]) for i in xrange(bc) if form.cleaned_data['blwl%d' % i] in aps_list_full]
                    ), np.array([aps_list_full.index(i) for i in 'Kingdra|??', 'Kabutops|??', 'Omastar|shell smash', 'Swampert-Mega|??'
                                 if form.cleaned_data["bl_rain"] and not int(form.cleaned_data["bl_wl_mode"])])),
                int(form.cleaned_data["bl_wl_mode"]),
                form.cleaned_data["blind"],
                form.cleaned_data["f"]
                )
                })
                return res
        
        else:
            
            form = coreForm(bc)(request.POST)
            reqdata = dict(init_def)
            for i in xrange(bc):
                cont = 'blwl%d' % i
                if cont in form.data:
                    reqdata.update({cont: form.data[cont]})
            for i in ["weights", "ck_dir", "bl_wl_mode", "blind", "gen_qty"]:
                if i in form.data:
                    reqdata.update({i: form.data[i]})
            
            if "add_blwl_field" in request.POST:
                bc += 1
            
            form = coreForm(bc, False)(initial=reqdata)
    
    else:
        
        form = coreForm(0, False)(initial=init_def)
        
    return render(request, 'corecontent.html', {'form': form})

@csrf_exempt
def team_generator(request):
    
    if request.method == 'POST':
            
        form = genForm(request.POST)
        if form.is_valid():
            return render(request, 'contentout.html', {'content':
            tg.team_generator(
            np.array(le(form.cleaned_data["weights"])),
            form.cleaned_data["ck_dir"],
            np.array([aps_list_full.index(i) for i in 'Kingdra|??', 'Kabutops|??', 'Omastar|shell smash', 'Swampert-Mega|??' if form.cleaned_data["bl_rain"]])
            )
            })
    
    else:
        
        form = genForm(initial={"bl_rain": True})
        
    return render(request, 'gencontent.html', {'form': form})

@csrf_exempt
def team_completer(request):
    
    init_def = {
    # "weights": str(WEIGHTS_DEF["Check"].tolist()) + " # Check Weights (Offense)",
    "bl_rain": True,
    "f": True
    }
    
    global aps_list_full
    
    if request.method == 'POST':
    
        pc = 1
        while "pkmn%d" % pc in request.POST:
            pc += 1
        bc = 0
        while "blwl%d" % bc in request.POST:
            bc += 1
        
        if "calculate" in request.POST:
            
            form = completeForm(pc, bc)(request.POST)
            if form.is_valid():
                res = render(request, 'contentout.html', {'content':
                tg.team_completer(
                np.array([aps_list_full.index(form.cleaned_data['pkmn%d' % i]) for i in xrange(pc)]),
                np.array(le(form.cleaned_data["weights"])),
                form.cleaned_data["ck_dir"],
                np.union1d(np.array(
                    [aps_list_full.index(form.cleaned_data['blwl%d' % i]) for i in xrange(bc) if form.cleaned_data['blwl%d' % i] in aps_list_full]
                    ), np.array([aps_list_full.index(i) for i in 'Kingdra|??', 'Kabutops|??', 'Omastar|shell smash', 'Swampert-Mega|??'
                                 if form.cleaned_data["bl_rain"] and not int(form.cleaned_data["bl_wl_mode"])])),
                int(form.cleaned_data["bl_wl_mode"]),
                form.cleaned_data["blind"],
                form.cleaned_data["f"]
                )
                })
                return res
        
        else:
            
            form = completeForm(pc, bc)(request.POST)
            reqdata = dict(init_def)
            for i in xrange(pc):
                cont = 'pkmn%d' % i
                if cont in form.data:
                    reqdata.update({cont: form.data[cont]})
            for i in xrange(bc):
                cont = 'blwl%d' % i
                if cont in form.data:
                    reqdata.update({cont: form.data[cont]})
            for i in ["weights", "ck_dir", "bl_wl_mode", "blind"]:
                if i in form.data:
                    reqdata.update({i: form.data[i]})
            
            if "add_pkmn_field" in request.POST:
                pc += 1
            
            if "add_blwl_field" in request.POST:
                bc += 1
            
            form = completeForm(pc, bc, False)(initial=reqdata)
    
    else:
        
        form = completeForm(1, 0, False)(initial=init_def)
        
    return render(request, 'completecontent.html', {'form': form})

@csrf_exempt
def replacement_suggestor(request):
    
    init_def = {
    # "weights": str(WEIGHTS_DEF["Check"].tolist()) + " # Check Weights (Offense)",
    "bl_rain": True,
    "f": True
    }
    
    global aps_list_full
    
    if request.method == 'POST':
    
        pc = 2
        while "pkmn%d" % pc in request.POST:
            pc += 1
        bc = 0
        while "blwl%d" % bc in request.POST:
            bc += 1
        
        if "calculate" in request.POST:
            
            form = replaceForm(pc, bc)(request.POST)
            if form.is_valid():
                res = render(request, 'contentout.html', {'content':
                tg.replacement_suggestor(
                np.array([aps_list_full.index(form.cleaned_data['pkmn%d' % i]) for i in xrange(pc)]),
                np.array(le(form.cleaned_data["weights"])),
                form.cleaned_data["ck_dir"],
                np.union1d(np.array(
                    [aps_list_full.index(form.cleaned_data['blwl%d' % i]) for i in xrange(bc) if form.cleaned_data['blwl%d' % i] in aps_list_full]
                    ), np.array([aps_list_full.index(i) for i in 'Kingdra|??', 'Kabutops|??', 'Omastar|shell smash', 'Swampert-Mega|??'
                                 if form.cleaned_data["bl_rain"] and not int(form.cleaned_data["bl_wl_mode"])])),
                int(form.cleaned_data["bl_wl_mode"]),
                form.cleaned_data["blind"],
                form.cleaned_data["f"]
                )
                })
                return res
        
        else:
            
            form = replaceForm(pc, bc)(request.POST)
            reqdata = dict(init_def)
            for i in xrange(pc):
                cont = 'pkmn%d' % i
                if cont in form.data:
                    reqdata.update({cont: form.data[cont]})
            for i in xrange(bc):
                cont = 'blwl%d' % i
                if cont in form.data:
                    reqdata.update({cont: form.data[cont]})
            for i in ["weights", "ck_dir", "bl_wl_mode", "blind"]:
                if i in form.data:
                    reqdata.update({i: form.data[i]})
            
            if "add_pkmn_field" in request.POST:
                pc += 1
            
            if "add_blwl_field" in request.POST:
                bc += 1
            
            form = replaceForm(pc, bc, False)(initial=reqdata)
    
    else:
        
        form = replaceForm(2, 0, False)(initial=init_def)
        
    return render(request, 'suggestcontent.html', {'form': form})

@csrf_exempt
def custom_generator(request):
    
    init_def = {
    # "weights": str(WEIGHTS_DEF["Check"].tolist()) + " # Check Weights (Offense)",
    "list_qty": 25,
    "bl_rain": True,
    "f": True
    }
    
    global aps_list_full
    
    if request.method == 'POST':
    
        pc = 0
        while "pkmn%d" % pc in request.POST:
            pc += 1
        bc = 0
        while "blwl%d" % bc in request.POST:
            bc += 1
        
        if "calculate" in request.POST:
            
            form = customForm(pc, bc)(request.POST)
            if form.is_valid():
                res = render(request, 'contentout.html', {'content':
                tg.custom_generator(
                np.array([aps_list_full.index(form.cleaned_data['pkmn%d' % i]) for i in xrange(pc)]),
                np.array(le(form.cleaned_data["weights"])),
                form.cleaned_data["ck_dir"],
                form.cleaned_data["gen_qty"],
                form.cleaned_data["list_qty"],
                int(form.cleaned_data["alg"]),
                np.union1d(np.array(
                    [aps_list_full.index(form.cleaned_data['blwl%d' % i]) for i in xrange(bc) if form.cleaned_data['blwl%d' % i] in aps_list_full]
                    ), np.array([aps_list_full.index(i) for i in 'Kingdra|??', 'Kabutops|??', 'Omastar|shell smash', 'Swampert-Mega|??'
                                 if form.cleaned_data["bl_rain"] and not int(form.cleaned_data["bl_wl_mode"])])),
                int(form.cleaned_data["bl_wl_mode"]),
                form.cleaned_data["blind"],
                form.cleaned_data["f"]
                )
                })
                return res
        
        else:
            
            form = customForm(pc, bc)(request.POST)
            reqdata = dict(init_def)
            for i in xrange(pc):
                cont = 'pkmn%d' % i
                if cont in form.data:
                    reqdata.update({cont: form.data[cont]})
            for i in xrange(bc):
                cont = 'blwl%d' % i
                if cont in form.data:
                    reqdata.update({cont: form.data[cont]})
            for i in ["gen_qty", "list_qty", "weights", "ck_dir", "alg", "bl_wl_mode", "blind"]:
                if i in form.data:
                    reqdata.update({i: form.data[i]})
            
            if "add_pkmn_field" in request.POST:
                pc += 1
            
            if "add_blwl_field" in request.POST:
                bc += 1
            
            form = customForm(pc, bc, False)(initial=reqdata)
    
    else:
        
        form = customForm(0, 0, False)(initial=init_def)
        
    return render(request, 'customcontent.html', {'form': form})

@csrf_exempt
def counterteam_generator(request):
    
    init_def = {
    "weights": str(WEIGHTS_DEF["Counter"].tolist()) + " # Counter Weights (Stall)",
    "bl_rain": True,
    "f": True
    }
    
    global aps_list_full
    
    if request.method == 'POST':
    
        pc = 0
        while "pkmn%d" % pc in request.POST:
            pc += 1
        cc = 1
        while "cntr%d" % cc in request.POST:
            cc += 1
        bc = 0
        while "blwl%d" % bc in request.POST:
            bc += 1
        
        if "calculate" in request.POST:
            
            form = counterForm(pc, cc, bc)(request.POST)
            if form.is_valid():
                res = render(request, 'contentout.html', {'content':
                tg.counterteam_generator(
                np.array([aps_list_full.index(form.cleaned_data['pkmn%d' % i]) for i in xrange(pc)]),
                np.array([aps_list_full.index(form.cleaned_data['cntr%d' % i]) for i in xrange(cc)]),
                form.cleaned_data["ck_dir"],
                np.array(le(form.cleaned_data["weights"])),
                form.cleaned_data["gen_qty"],
                np.union1d(np.array(
                    [aps_list_full.index(form.cleaned_data['blwl%d' % i]) for i in xrange(bc) if form.cleaned_data['blwl%d' % i] in aps_list_full]
                    ), np.array([aps_list_full.index(i) for i in 'Kingdra|??', 'Kabutops|??', 'Omastar|shell smash', 'Swampert-Mega|??'
                                 if form.cleaned_data["bl_rain"] and not int(form.cleaned_data["bl_wl_mode"])])),
                int(form.cleaned_data["bl_wl_mode"]),
                form.cleaned_data["f"]
                )
                })
                return res
        
        else:
            
            form = counterForm(pc, cc, bc)(request.POST)
            reqdata = dict(init_def)
            for i in xrange(pc):
                cont = 'pkmn%d' % i
                if cont in form.data:
                    reqdata.update({cont: form.data[cont]})
            for i in xrange(cc):
                cont = 'cntr%d' % i
                if cont in form.data:
                    reqdata.update({cont: form.data[cont]})
            for i in xrange(bc):
                cont = 'blwl%d' % i
                if cont in form.data:
                    reqdata.update({cont: form.data[cont]})
            for i in ["gen_qty", "weights", "ck_dir", "bl_wl_mode"]:
                if i in form.data:
                    reqdata.update({i: form.data[i]})
            
            if "add_pkmn_field" in request.POST:
                pc += 1
            
            if "add_cntr_field" in request.POST:
                cc += 1
            
            if "add_blwl_field" in request.POST:
                bc += 1
            
            form = counterForm(pc, cc, bc, False)(initial=reqdata)
    
    else:
        
        form = counterForm(0, 1, 0, False)(initial=init_def)
        
    return render(request, 'countercontent.html', {'form': form})

@csrf_exempt
def team_comparer(request):  # the doozy.
    
    init_def = {
    # "weights": str(WEIGHTS_DEF["Check"].tolist()) + " # Check Weights (Offense)"
    }
    
    global aps_list_full
    
    if request.method == 'POST':
        
        tc = []
        while "pkmn%d_0" % len(tc) in request.POST:
            tc.append(1)
            while "pkmn%d_%d" % (len(tc)-1, tc[-1]) in request.POST:
                tc[-1] += 1
        
        if "calculate" in request.POST:
            
            form = compareForm(tc)(request.POST)
            if form.is_valid():
                
                res = render(request, 'contentout.html', {'content':
                tg.team_comparer(
                [
                np.array([
                aps_list_full.index(form.cleaned_data["pkmn%d_%d" % (team_idx, pkmn_idx)])
                for pkmn_idx in xrange(tc[team_idx])
                ])
                for team_idx in xrange(len(tc))
                ],
                form.cleaned_data["ck_dir"],
                np.array(le(form.cleaned_data["weights"]))
                )
                })
                return res
        
        else:
            
            form = compareForm(tc)(request.POST)
            reqdata = dict(init_def)
            for t in xrange(len(tc)):
                for i in xrange(tc[t]):
                    cont = 'pkmn%d_%d' % (t, i)
                    if cont in form.data:
                        reqdata.update({cont: form.data[cont]})
            for i in ["weights", "ck_dir"]:
                if i in form.data:
                    reqdata.update({i: form.data[i]})
            for t in xrange(len(tc)):
                if "Add Pokemon Field To Team %d" % (t+1) in request.POST:
                    tc[t] += 1
            if "add_team" in request.POST:
                tc.append(1)
            
            form = compareForm(tc, False)(initial=reqdata)
    
    else:
        
        form = compareForm([1], False)(initial=init_def)
        
    return render(request, 'comparecontent.html', {'form': form, 'team_count': ["Add Pokemon Field To Team %d" % (i+1) for i in xrange(len(tc) if "tc" in locals() else 1)]})

@csrf_exempt
def check_map(request):
    
    global aps_list_full
    
    if request.method == 'POST':
    
        pc0 = 0
        while "pkmn0_%d" % pc0 in request.POST:
            pc0 += 1
        pc1 = 0
        while "pkmn1_%d" % pc1 in request.POST:
            pc1 += 1
        
        if "calculate" in request.POST:
            
            form = mapForm(pc0, pc1)(request.POST)
            if form.is_valid():
                res = render(request, 'contentout.html', {'content':
                tg.check_map(
                np.array([aps_list_full.index(form.cleaned_data['pkmn0_%d' % i]) for i in xrange(pc0)]),
                np.array([aps_list_full.index(form.cleaned_data['pkmn1_%d' % i]) for i in xrange(pc1)])
                )
                })
                return res
        
        else:
            
            form = mapForm(pc0, pc1)(request.POST)
            reqdata = {}
            for i in xrange(pc0):
                cont = 'pkmn0_%d' % i
                if cont in form.data:
                    reqdata.update({cont: form.data[cont]})
            for i in xrange(pc1):
                cont = 'pkmn1_%d' % i
                if cont in form.data:
                    reqdata.update({cont: form.data[cont]})
            
            if "add_pkmn_field0" in request.POST:
                pc0 += 1
            
            if "add_pkmn_field1" in request.POST:
                pc1 += 1
            
            form = mapForm(pc0, pc1, False)(initial=reqdata)
    
    else:
        
        form = mapForm(1, 1, False)(initial={})
        
    return render(request, 'mapcontent.html', {'form': form})

def set_usage_stats(request):
    return render(request, 'suscontent.html', {'content': tg.wformat(tg.althigh(sus_res))})

def how_to_update(request):
    return render(request, 'htucontent.html')

def credits(request):
    return render(request, 'creditcontent.html')

def about(request):
    return render(request, 'about.html', {
    'content': ('%s/20%s' % (usage_origin[1], usage_origin[0]))
    if isinstance(usage_origin, tuple) else usage_origin
    })