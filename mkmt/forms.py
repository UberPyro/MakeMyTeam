from django import forms
from .fields import ListTextWidget

from django.core.cache import cache
# import numpy as np

aps_list_full = cache.get("init")["aps_list_full"]
WEIGHTS_DEF = cache.get("init")["WEIGHTS_DEF"]
wei_init = [str(WEIGHTS_DEF["Check"].tolist()) + " # Check Weights (Offense)", str(WEIGHTS_DEF["Counter"].tolist()) + " # Counter Weights (Stall)"]

def brmtForm(pkmn_field_qty, fillbool=True):
    
    class MadeForm(forms.Form):
        
        
        for i in xrange(pkmn_field_qty):
            locals()["pkmn%d" % i] = forms.CharField(label='Pokemon #%d' % (i+1),
            required=fillbool,
            widget=ListTextWidget(data_list=aps_list_full, name='Pokemon List')
            )
        
        ck_weight = forms.CharField(label='Check Weighting')
        cntr_weight = forms.CharField(label='Counter Weighting')
        ck_dir = forms.ChoiceField(label='View', choices=((('by', 'NSI/SSI/GSI By Data'), ('to', 'NSI/SSI/GSI To Data'))))
        blind = forms.BooleanField(label='Make Usage Blind', required=False)
    
    
    return MadeForm

class mcrForm(forms.Form):
    
    ck_weight = forms.CharField(label='Check Weighting')
    cntr_weight = forms.CharField(label='Counter Weighting')
    ck_dir = forms.ChoiceField(label='View', choices=(('to', 'NSI/SSI/GSI To Data'), ('by', 'NSI/SSI/GSI By Data')))
    ck_lv = forms.ChoiceField(label='Check Level', choices=(('Check', 'Check'), ('Counter', 'Counter')))
    blind = forms.BooleanField(label='Make Usage Blind', required=False)

class pkmnDataForm(forms.Form):
    
    pkmn = forms.CharField(label='Pokemon', widget=ListTextWidget(data_list=aps_list_full, name='Pokemon List'))

def partnerForm(blwl_field_qty, fillbool=True):
    
    class MadeForm(forms.Form):
        
        
        pkmn = forms.CharField(label='Pokemon', required=fillbool, widget=ListTextWidget(data_list=aps_list_full, name='Pokemon List'))
        weights = forms.CharField(label='Weighting', required=fillbool, widget=ListTextWidget(data_list=wei_init, name='Weights List'))
        ck_dir = forms.ChoiceField(label='Optimize', choices=(('to', 'NSI/SSI/GSI To Data'), ('by', 'NSI/SSI/GSI By Data')))
        
        for i in xrange(blwl_field_qty):
            locals()["blwl%d" % i] = forms.CharField(label='Blacklist/Whitelist #%d' % (i+1),
            required=False,
            widget=ListTextWidget(data_list=aps_list_full, name='Blacklist/Whitelist List')
            )
        
        bl_wl_mode = forms.ChoiceField(label='Blacklist/Whitelist Mode', choices=((0, 'Blacklist'), (1, 'Whitelist')))
        bl_rain = forms.BooleanField(label='Blacklist Rain', required=False)
        blind = forms.BooleanField(label='Make Usage Blind', required=False)
        f = forms.BooleanField(label='Filter Duplicate Species, Megas, and Z-Movers', required=False)
    
    return MadeForm

def coreForm(blwl_field_qty, fillbool=True):
    
    class MadeForm(forms.Form):
        
        
        weights = forms.CharField(label='Weighting', required=fillbool, widget=ListTextWidget(data_list=wei_init, name='Weights List'))
        ck_dir = forms.ChoiceField(label='Optimize', choices=(('to', 'NSI/SSI/GSI To Data'), ('by', 'NSI/SSI/GSI By Data')))
        gen_qty = forms.IntegerField(label = 'Number Of Pokemon To Generate', required=fillbool)
        
        for i in xrange(blwl_field_qty):
            locals()["blwl%d" % i] = forms.CharField(label='Blacklist/Whitelist #%d' % (i+1),
            required=False,
            widget=ListTextWidget(data_list=aps_list_full, name='Blacklist/Whitelist List')
            )
        
        bl_wl_mode = forms.ChoiceField(label='Blacklist/Whitelist Mode', choices=((0, 'Blacklist'), (1, 'Whitelist')))
        bl_rain = forms.BooleanField(label='Blacklist Rain', required=False)
        blind = forms.BooleanField(label='Make Usage Blind', required=False)
        f = forms.BooleanField(label='Filter Duplicate Species, Megas, and Z-Movers', required=False)
    
    return MadeForm

class genForm(forms.Form):
    
    
    weights = forms.ChoiceField(label='Weighting', choices=zip(wei_init, wei_init))
    ck_dir = forms.ChoiceField(label='Optimize', choices=(('to', 'NSI/SSI/GSI To Data'), ('by', 'NSI/SSI/GSI By Data')))
    bl_rain = forms.BooleanField(label='Blacklist Rain', required=False)

def completeForm(pkmn_field_qty, blwl_field_qty, fillbool=True):
    
    class MadeForm(forms.Form):
        
        
        for i in xrange(pkmn_field_qty):
            locals()["pkmn%d" % i] = forms.CharField(label='Pokemon #%d' % (i+1),
            required=fillbool,
            widget=ListTextWidget(data_list=aps_list_full, name='Pokemon List')
            )
        
        weights = forms.CharField(label='Weighting', required=fillbool, widget=ListTextWidget(data_list=wei_init, name='Weights List'))
        ck_dir = forms.ChoiceField(label='Optimize', choices=(('to', 'NSI/SSI/GSI To Data'), ('by', 'NSI/SSI/GSI By Data')))
        
        for i in xrange(blwl_field_qty):
            locals()["blwl%d" % i] = forms.CharField(label='Blacklist/Whitelist #%d' % (i+1),
            required=False,
            widget=ListTextWidget(data_list=aps_list_full, name='Blacklist/Whitelist List')
            )
        
        bl_wl_mode = forms.ChoiceField(label='Blacklist/Whitelist Mode', choices=((0, 'Blacklist'), (1, 'Whitelist')))
        bl_rain = forms.BooleanField(label='Blacklist Rain', required=False)
        blind = forms.BooleanField(label='Make Usage Blind', required=False)
        f = forms.BooleanField(label='Filter Duplicate Species, Megas, and Z-Movers', required=False)
    
    return MadeForm

def replaceForm(pkmn_field_qty, blwl_field_qty, fillbool=True):
    
    class MadeForm(forms.Form):
        
        
        for i in xrange(pkmn_field_qty):
            locals()["pkmn%d" % i] = forms.CharField(label='Pokemon #%d' % (i+1),
            required=fillbool,
            widget=ListTextWidget(data_list=aps_list_full, name='Pokemon List')
            )
        
        weights = forms.CharField(label='Weighting', required=fillbool, widget=ListTextWidget(data_list=wei_init, name='Weights List'))
        ck_dir = forms.ChoiceField(label='Optimize', choices=(('to', 'NSI/SSI/GSI To Data'), ('by', 'NSI/SSI/GSI By Data')))
        
        for i in xrange(blwl_field_qty):
            locals()["blwl%d" % i] = forms.CharField(label='Blacklist/Whitelist #%d' % (i+1),
            required=False,
            widget=ListTextWidget(data_list=aps_list_full, name='Blacklist/Whitelist List')
            )
        
        bl_wl_mode = forms.ChoiceField(label='Blacklist/Whitelist Mode', choices=((0, 'Blacklist'), (1, 'Whitelist')))
        bl_rain = forms.BooleanField(label='Blacklist Rain', required=False)
        blind = forms.BooleanField(label='Make Usage Blind', required=False)
        f = forms.BooleanField(label='Filter Duplicate Species, Megas, and Z-Movers', required=False)
    
    return MadeForm

def customForm(pkmn_field_qty, blwl_field_qty, fillbool=True):
    
    class MadeForm(forms.Form):
        
        
        for i in xrange(pkmn_field_qty):
            locals()["pkmn%d" % i] = forms.CharField(label='Pokemon #%d' % (i+1),
            required=fillbool,
            widget=ListTextWidget(data_list=aps_list_full, name='Pokemon List')
            )
        
        weights = forms.CharField(label='Weighting', required=fillbool, widget=ListTextWidget(data_list=wei_init, name='Weights List'))
        ck_dir = forms.ChoiceField(label='Optimize', choices=(('to', 'NSI/SSI/GSI To Data'), ('by', 'NSI/SSI/GSI By Data')))
        gen_qty = forms.IntegerField(label = 'Number Of Pokemon To Generate', required=fillbool)
        list_qty = forms.IntegerField(label = 'Number Of Teams To Display', required=fillbool)
        alg = forms.ChoiceField(label='Algorithm', choices=((0, 'Combinational'), (1, 'Recursive')))
        
        for i in xrange(blwl_field_qty):
            locals()["blwl%d" % i] = forms.CharField(label='Blacklist/Whitelist #%d' % (i+1),
            required=False,
            widget=ListTextWidget(data_list=aps_list_full, name='Blacklist/Whitelist List')
            )
        
        bl_wl_mode = forms.ChoiceField(label='Blacklist/Whitelist Mode', choices=((0, 'Blacklist'), (1, 'Whitelist')))
        bl_rain = forms.BooleanField(label='Blacklist Rain', required=False)
        blind = forms.BooleanField(label='Make Usage Blind', required=False)
        f = forms.BooleanField(label='Filter Duplicate Species, Megas, and Z-Movers', required=False)
    
    return MadeForm

def counterForm(pkmn_field_qty, cntr_field_qty, blwl_field_qty, fillbool=True):
    
    class MadeForm(forms.Form):
        
        
        for i in xrange(pkmn_field_qty):
            locals()["pkmn%d" % i] = forms.CharField(label='Pokemon (on team being generated) #%d' % (i+1),
            required=fillbool,
            widget=ListTextWidget(data_list=aps_list_full, name='Pokemon List')
            )
        
        for i in xrange(cntr_field_qty):
            locals()["cntr%d" % i] = forms.CharField(label='Pokemon To Counter #%d' % (i+1),
            required=fillbool,
            widget=ListTextWidget(data_list=aps_list_full, name='Counter List')
            )
        
        weights = forms.CharField(label='Weighting', required=fillbool, widget=ListTextWidget(data_list=wei_init, name='Weights List'))
        ck_dir = forms.ChoiceField(label='Optimize', choices=(('to', 'NSI/SSI/GSI To Data'), ('by', 'NSI/SSI/GSI By Data')))
        gen_qty = forms.IntegerField(label = 'Number Of Pokemon To Generate', required=fillbool)
        
        for i in xrange(blwl_field_qty):
            locals()["blwl%d" % i] = forms.CharField(label='Blacklist/Whitelist #%d' % (i+1),
            required=False,
            widget=ListTextWidget(data_list=aps_list_full, name='Blacklist/Whitelist List')
            )
        
        bl_wl_mode = forms.ChoiceField(label='Blacklist/Whitelist Mode', choices=((0, 'Blacklist'), (1, 'Whitelist')))
        bl_rain = forms.BooleanField(label='Blacklist Rain', required=False)
        f = forms.BooleanField(label='Filter Duplicate Species, Megas, and Z-Movers', required=False)
    
    return MadeForm

def compareForm(team_field_qty, fillbool=True):
    
    class MadeForm(forms.Form):
        
        
        for t in xrange(len(team_field_qty)):
            for i in xrange(team_field_qty[t]):
                locals()["pkmn%d_%d" % (t, i)] = forms.CharField(label='Pokemon #%d (Team %d)' % (i+1, t+1),
                required=fillbool,
                widget=ListTextWidget(data_list=aps_list_full, name='Pokemon List')
                )
        
        weights = forms.CharField(label='Weighting', required=fillbool, widget=ListTextWidget(data_list=wei_init, name='Weights List'))
        ck_dir = forms.ChoiceField(label='View', choices=(('to', 'NSI/SSI/GSI To Data'), ('by', 'NSI/SSI/GSI By Data')))
    
    return MadeForm

def mapForm(pkmn_field_qty0, pkmn_field_qty1, fillbool=True):
    
    class MadeForm(forms.Form):
        
        
        for i in xrange(pkmn_field_qty0):
            locals()["pkmn0_%d" % i] = forms.CharField(label='Pokemon #%d (Team 1)' % (i+1),
            required=fillbool,
            widget=ListTextWidget(data_list=aps_list_full, name='Pokemon List')
            )
        
        for i in xrange(pkmn_field_qty1):
            locals()["pkmn1_%d" % i] = forms.CharField(label='Pokemon #%d (Team 2)' % (i+1),
            required=fillbool,
            widget=ListTextWidget(data_list=aps_list_full, name='Pokemon List')
            )
    
    return MadeForm