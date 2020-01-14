from django.shortcuts import render
from django.views.generic import TemplateView
from .wowma_api import wowma_api

class DashBoard(TemplateView):
    template_name = 'wowma_dashboard.html'
    
    def get(self, request, *args, **kwargs):
        limit = 10
        if not 'offset' in request.GET:
            offset = 0
        else:
            offset = request.GET.get('offset')
            if not offset.isdecimal():
                pass
            else:
                offset = int(offset)
        context = self.get_context_data(**kwargs)
        try:
            object_list = wowma_api.search_item_info(limit, offset)
        except Exception as e:
            print(e)
        else:
            context['object_list'] = object_list
        
        return self.render_to_response(context)
