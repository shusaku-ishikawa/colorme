from django.shortcuts import render
from django.views.generic import TemplateView
from .wowma_api import wowma_api

class DashBoard(TemplateView):
    template_name = 'wowma_dashboard.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        res = wowma_api.search_item_info(10, 10)
        return context        