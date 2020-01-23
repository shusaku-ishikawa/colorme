from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .wowma_api import WowmaApi
from django.conf import settings
from .enums import *
from .forms import *
from core.models import *
from django.contrib.auth.mixins import LoginRequiredMixin
import csv
from io import TextIOWrapper, StringIO
from django.contrib import messages
class DashBoard(LoginRequiredMixin, TemplateView):
    template_name = 'wowma_dashboard.html'
     
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['pagename'] = 'dashboard'
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
            obj = AuthInfo.objects.get(client_id = request.user.wowma_auth.client_id)
            obj.delete()
            messages.success(request, '認証情報を削除しました')
            return redirect('wowma:dashboard')
        else:
           pass
class Search(TemplateView):
    template_name = 'wowma_searchitems.html'
     
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        limit = ITEMS_PER_PAGE
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
            wowma_api = WowmaApi(request.user.wowma_auth)
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

class Upload(LoginRequiredMixin, TemplateView):
    template_name = 'wowma_upload.html'
    
    def get(self, request, *args, **kwargs):
        if not request.user.wowma_auth:
            messages.error(request, '認証情報が登録されていません')
            return redirect('wowma:dashboard')
        context = super().get_context_data(**kwargs)
        context['pagename'] = 'upload'
        return super().render_to_response(context)
    
    def dictize_params(self, cols):
        ret = {}
        ret['item_id'] = cols[UploadFileColumns.item_id]
        ret['identifier'] = cols[UploadFileColumns.identifier]
        ret['category_id'] = cols[UploadFileColumns.category_id]
        ret['title'] = cols[UploadFileColumns.title]
        ret['price'] = cols[UploadFileColumns.price]
        ret['item_tax_type'] = cols[UploadFileColumns.item_tax_type]
        ret['detail'] = cols[UploadFileColumns.detail]
        ret['variations'] = [{'variation_id': cols[UploadFileColumns.variation_start + 2*i], 'variation': cols[UploadFileColumns.variation_start + 2*i + 1], 'variation_stock': cols[UploadFileColumns.variation_stock_start + i]} for i in range(20) if cols[UploadFileColumns.variation_start + 2*i + 1] != '']
        for i in range(20):
            if not cols[UploadFileColumns.img_origin_start + i] or cols[UploadFileColumns.img_origin_start + i] == '':
                break
            key = f'img{i + 1}_origin'
            ret[key] = cols[UploadFileColumns.img_origin_start + i]
        ret['stock'] = cols[UploadFileColumns.stock]
        ret['list_order'] = cols[UploadFileColumns.list_order]
        ret['visible'] = cols[UploadFileColumns.visible]
        ret['delivery_company_id'] = cols[UploadFileColumns.delivery_company_id]
        return ret
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        f = request.FILES.get('uploadfile')
        form_data = TextIOWrapper(f, encoding='utf-8')
        csv_file = csv.reader(form_data)
        items_to_register = []

        all_ok = True
        for index, line in enumerate(csv_file):
            if index == 0:
                continue
            param_dict = self.dictize_params(line)
            item = Item(param_dict)
            if not item.validate_for_add(index):
                all_ok = False
            items_to_register.append(item)
        if not all_ok:
            messages.error(request, 'ファイルにエラーがありました')
            context['errors'] = [item for item in items_to_register if not item.valid]
            return self.render_to_response(context)
        else:
            for item in items_to_register:
                if item.valid:
                    if not item.item_id: # if new
                        item.add(request.user.wowma_auth)
                    else: # if edit
                        item.edit(request.user.wowma_auth)
            runtimeerrors = [item for item in items_to_register if not item.valid]
            if len(runtimeerrors) > 0:
                messages.error(request, '登録時にエラーがありました')
                context['errors'] = runtimeerrors
                return self.render_to_response(context)
            else:
                messages.success(request, '登録が完了しました')
                return redirect('wowma:upload')

            
