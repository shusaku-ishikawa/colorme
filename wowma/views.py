from django.shortcuts import render
from django.views.generic import TemplateView
from .wowma_api import wowma_api
from django.conf import settings

class DashBoard(TemplateView):
    template_name = 'wowma_dashboard.html'
     
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        limit = settings.ITEMS_PER_PAGE
        if 'action' in request.GET and request.GET.get('action') == 'search':
            # if new search request
            if 'searchparams' in request.session:
                del request.session['searchparams']
            itemname = request.GET.get('itemname') or ''
            itemcode = request.GET.get('itemcode') or ''
            searchparams = {}
            if itemname != "":
                searchparams['itemname'] = request.GET.get('itemname')
            if itemcode != "":
                searchparams['itemcode'] = request.GET.get('itemcode')
            request.session['searchparams'] = searchparams
        else:
            searchparams = request.session['searchparams'] if 'searchparams' in request.session else None
            
        if searchparams:
            if not 'page' in request.GET:
                page = 1
            else:
                page = request.GET.get('page')
                if not page.isdecimal():
                    pass
                else:
                    page = int(page) 
            context['searchparams'] = searchparams        
            context['search_result'] = wowma_api.search_item_info(limit, page, searchparams)
       
        return self.render_to_response(context)
