from django.shortcuts import render
from django.views.generic import TemplateView
from .wowma_api import wowma_api

class DashBoard(TemplateView):
    template_name = 'wowma_dashboard.html'
    def set_pagination(self, context, current_page, max_count):
        context['current_page'] = current_page
         
    def get(self, request, *args, **kwargs):
        limit = 10
        
        if not 'page' in request.GET:
            page = 1
        else:
            page = request.GET.get('page')
            if not page.isdecimal():
                pass
            else:
                page = int(page)
        context = self.get_context_data(**kwargs)
        context['search_result'] = wowma_api.search_item_info(page)
       
        return self.render_to_response(context)
