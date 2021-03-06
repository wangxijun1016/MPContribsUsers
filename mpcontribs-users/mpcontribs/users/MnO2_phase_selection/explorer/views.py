"""This module provides the views for the MnO2_phase_selection explorer interface."""

import json
from bson import ObjectId
from django.shortcuts import render_to_response, redirect
try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse
from django.template import RequestContext
from mpcontribs.rest.views import get_endpoint
from mpcontribs.io.core.components import render_dataframe
from mpcontribs.io.core.recdict import render_dict
from webtzite.models import RegisteredUser

def index(request):
    ctx = RequestContext(request)
    if request.user.is_authenticated():
        user = RegisteredUser.objects.get(username=request.user.username)
        from ..rest.rester import Mno2PhaseSelectionRester
        with Mno2PhaseSelectionRester(user.api_key, endpoint=get_endpoint(request)) as mpr:
            try:
                prov = mpr.get_provenance()
                ctx['title'] = prov.pop('title')
                ctx['provenance'] = render_dict(prov, webapp=True)
                tables = {}
                for phase in mpr.get_phases():
                    df = mpr.get_contributions(phase=phase)
                    tables[phase] = render_dataframe(df, webapp=True)
                ctx['tables'] = tables
            except Exception as ex:
                ctx.update({'alert': str(ex)})
    else:
        return redirect('{}?next={}'.format(reverse('cas_ng_login'), request.path))
    return render_to_response("MnO2_phase_selection_explorer_index.html", ctx)
