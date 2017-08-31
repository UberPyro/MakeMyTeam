# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.core.cache import cache

import numpy as np

array_keys = []
def save_key(k):
    global array_keys
    array_keys.append(k)
    return k

class mkmtConfig(AppConfig):
    name = 'mkmt'
    verbose_name = "MakeMyTeam"
    def ready(self):
        global array_keys
        from mkmt_init import (
        sus, sus_array, sus_array_blind, sus_dict_full, sus_res,
        sum_dict,
        apsnd, apsn, aps_list_full, apsnf, 
        apply_weights, WEIGHTS_DEF,
        zpad,
        COMBO_LIMIT, COMBO_LIMIT_CT,
        checkp, checks,
        usage_origin,
        )
        cache.set("init", {k: v for k, v in locals().iteritems() if k != "self"}, None)