from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from .wowma_api import WowmaApi
from django.conf import settings
from .enums import *
from .forms import *
from core.models import *
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin
import csv
from io import TextIOWrapper, StringIO
from colorme.models import Item as colorme_Item
from django.contrib import messages


class DashBoard(LoginRequiredMixin, TemplateView):
    template_name = 'wowma_dashboard.html'
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['pagename'] = 'wowma_dashboard'
        context['form'] = AuthInfoModelForm()

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        params = request.POST.copy()
        operation = params.pop('operation')[0]
        if operation == 'add':
            form = AuthInfoModelForm(params)
            if form.is_valid():
                instance = form.save()
                user = User.objects.get(pk = request.user.pk)
                user.wowma_auth = instance
                user.save()
                messages.success(request, '認証情報を作成しました')
                return redirect('wowma:dashboard')
            else:
                print(form.errors)
                context['form'] = form
                return self.render_to_response(context)
        elif operation == 'delete':
            obj = AuthInfo.objects.get(application_key = request.user.wowma_auth.application_key)
            obj.delete()
            messages.success(request, '認証情報を削除しました')
            return redirect('wowma:dashboard')
        else:
           pass
class Search(LoginRequiredMixin, ListView):
    template_name = 'wowma_searchitems.html'
    model = Item
    paginate_by = 3

    def get_queryset(self, **kwargs):
        self.queryset = self.model.objects.filter(user = self.request.user)
        if kwargs['q']:
            self.queryset = self.queryset.filter(itemName__icontains = kwargs['q'])
        queryset = super().get_queryset()
        return queryset

    def get_context_data(self, **kwargs):
        object_list = self.get_queryset(**kwargs)
        context = super().get_context_data(object_list = object_list, **kwargs)
        context['pagename'] = 'wowma_search'
        context['q'] = kwargs['q']
        return context

    def get(self, request, *args, **kwargs):
        if 'action' in request.GET and request.GET.get('action') == 'search': 
            if 'q' in request.session:
                del request.session['q']
            q = request.GET.get('q') or ''
            request.session['q'] = q
        else:
            if 'q' in request.session:
                del request.session['q']
            q = request.session['q'] if 'q' in request.session else None
        
        kwargs['q'] = q

        self.object_list = self.get_queryset(**kwargs)
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class Delete(LoginRequiredMixin, TemplateView):
    template_name = 'wowma_delete.html'
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        operation = request.GET.get('operation')
        selected_items = request.GET.getlist('selected_items[]')
        context['selected_items'] = selected_items
        context['operation'] = operation
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        selected_items = request.POST.getlist('selected_items[]')
        operation = request.POST.get('operation')

        wowma_api = WowmaApi(request.user.wowma_auth)

        for lot_number in selected_items:
            item  = Item(lot_number)
            if operation == 'delete':
                func = wowma_api.delete_item
            elif operation in ['offsale', 'onsale']:
                item.sale_status = SALE_STATUS_ONSALE if operation == 'onsale' else SALE_STATUS_OFFSALE
                func = wowma_api.update_item

            if not func(item):
                messages.error(request, item.error)
                print(item.error)
            else: # if success
                messages.success(request, f'{item.lot_number}を{operation}しました')
        return redirect('wowma:search')

class ShopCategories(LoginRequiredMixin, ListView):
    model = ShopCategory
    template_name = 'wowma_shopcategories.html'

class Categories(LoginRequiredMixin, ListView):
    template_name = 'wowma_categories.html'
    #form_class = CategoryUploadFileForm
    model = Category
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagename'] = 'wowma_categories'
        return context

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    # def post(self, request, *args, **kwargs):
    #     context = self.get_context_data(**kwargs)
    #     form = self.form_class(request.POST, request.FILES)
    #     if not form.is_valid():
    #         context['form'] = form
    #         return self.render_to_response(context)
    #     form.save(commit = True)
    #     messages.success(request, '完了しました。')
    #     return redirect('wowma:categories')

class DeleteShopCategory(LoginRequiredMixin, TemplateView):
    template_name = 'wowma_delete_shopcategories.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        selected_categories = request.GET.getlist('selected_shopcategories[]')
        shopcategories = []
        for shopcategory_id in selected_shopcategories:
            shopcategories.append(ShopCategory.objects.get(shopCategoryId = shopcategory_id))
        context['shopcategories_to_delete'] = shopcategories
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        wowma_api = WowmaApi(request.user.wowma_auth)
        shopcategories_to_delete = request.POST.getlist('shopcategories_to_delete[]')
        for shopcategory_id in shopcategories_to_delete:
            try:
                r = wowma_api.delete_shopcategory(shopcategory_id)
            except Exception as e:
                messages.error(request, str(e))
            else: # if success
                print('category successfully deleted')
                ShopCategory.objects.get(shopCategoryId = shopcategory_id).delete()
                messages.success(request, f'{shopcategory_id}を削除しました')
        return redirect('wowma:shopcategories')
       
