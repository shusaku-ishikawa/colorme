from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView, ListView
from django.conf import settings
from .models import *
from .thebase_api import ThebaseApi
from core.models import User
from .enums import *
from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin
import csv
from io import TextIOWrapper, StringIO
from .forms import *
class DashBoard(LoginRequiredMixin, TemplateView):
    template_name = 'thebase_dashboard.html'
     
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['pagename'] = 'thebase_dashboard'
        context['form'] = OauthModelForm()

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        params = request.POST.copy()
        operation = params.pop('operation')[0]
        if operation == 'add':
            form = OauthModelForm(params)
            if form.is_valid():
                instance = form.save()
                user = User.objects.get(pk = request.user.pk)
                user.thebase_auth = instance
                user.save()
                messages.success(request, '認証情報を作成しました')
                return redirect('thebase:dashboard')
            else:
                print(form.errors)
                context['form'] = form
                return self.render_to_response(context)
        elif operation == 'delete':
            obj = Oauth.objects.get(client_id = request.user.thebase_auth.client_id)
            obj.delete()
            messages.success(request, '認証情報を削除しました')
            return redirect('thebase:dashboard')
        else:
            print(operation)
            print('hogehoge')
class Authorize(LoginRequiredMixin, TemplateView):
    template_name = 'thebase_dashboard.html'
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['pagename'] = 'thebase_authorize'
        if 'code' in request.GET: # if authorized
            authorization_code = request.GET.get('code')
            request.user.thebase_auth.set_authorization_code(authorization_code)
            try:
                request.user.thebase_auth.get_access_token(GRANT_TYPE_AUTHORIZATION_CODE)
            except Exception as e:
                context['error'] = str(e)
                messages.error(request, str(e))
                return self.render_to_response(context)
            else:
                messages.success(request, '認可コードを取得しました')
                return redirect('thebase:dashboard')
        elif 'error_denied' in request.GET: # if error
            context['error'] = '許可されませんでした'
            messages.error(request, '認可されませんでした')
            return render_to_response(context)

        elif 'refresh' in request.GET: # if refresh error
            try:
                request.user.thebase_auth.get_access_token(GRANT_TYPE_REFRESH_TOKEN)
            except Exception as e:
                context['error'] = str(e)
                messages.error(request, str(e))
                return self.render_to_response(context)
            else:
                messages.success(request, 'リフレッシュに成功しました')
                return redirect('thebase:dashboard')

        else: # if new then redirect authorization page
            if not request.user.thebase_auth:
                context['error'] = 'oauth情報を登録してから再度実行してください'
                return self.render_to_response(context)
            else:
                redirect_url = request.user.thebase_auth.authorize()
                return redirect(redirect_url)

class Categories(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'thebase_categories.html'
    def get_queryset(self, **kwargs):
        return self.model.objects.filter(user = self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagename'] = 'thebase_categories'

class Search(LoginRequiredMixin, ListView):
    model = Item
    template_name = 'thebase_searchitems.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['pagename'] = 'thebase_search'
        context['q'] = kwargs['q']
        return context

    def get_queryset(self, **kwargs):
        object_list = self.model.objects.filter(user = self.request.user)
        if kwargs['q']:
            object_list = object_list.filter(item_name__icontains = kwargs['q'])
        return object_list

    def get(self, request, *args, **kwargs):
        if 'action' in request.GET and request.GET.get('action') == 'search': 
            if 'q' in request.session:
                del request.session['q']
            q = request.GET.get('q') or ''
            request.session['q'] = q
        else:
            q = request.session['q'] if 'q' in request.session else None
        
        kwargs['q'] = q
        self.object_list = self.get_queryset(**kwargs)
        context = self.get_context_data(**kwargs)
        
        return self.render_to_response(context)

class Delete(LoginRequiredMixin, TemplateView):
    template_name = 'thebase_delete.html'
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        operation = request.GET.get('operation')
        selected_items = request.GET.getlist('selected_items[]')
        items = []
        for item_id in selected_items:
            items.append(Item.objects.get(item_id = item_id))
        context['items_to_delete'] = items
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        thebase_api = ThebaseApi(request.user.thebase_auth)
        items_to_delete = request.POST.getlist('items_to_delete[]')
        for item_id in items_to_delete:
            try:
                thebase_api.delete(item_id)
            except Exception as e:
                messages.error(request, str(e))
            else: # if success
                print('item successfully deleted')
                messages.success(request, f'{item_id}を削除しました')
        return redirect('thebase:search')

class DeleteCategory(LoginRequiredMixin, TemplateView):
    template_name = 'thebase_delete_categories.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        selected_categories = request.GET.getlist('selected_categories[]')
        categories = []
        for category_id in selected_categories:
            categories.append(Category.objects.get(category_id = category_id))
        context['categories_to_delete'] = categories
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        thebase_api = ThebaseApi(request.user.thebase_auth)
        categories_to_delete = request.POST.getlist('categories_to_delete[]')
        for category_id in categories_to_delete:
            try:
                r = thebase_api.delete_category(category_id)
                if not thebase_api.validate_response(r):
                    if thebase_api.error == '不正なcategory_idです。':
                        pass
                    else:
                        raise Exception(f'カテゴリ削除中にエラー {thebase_api.error}')
            except Exception as e:
                messages.error(request, str(e))
            else: # if success
                print('category successfully deleted')
                Category.objects.get(category_id = category_id).delete()
                messages.success(request, f'{category_id}を削除しました')
        return redirect('thebase:categories')
       
