from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .wowma_api import WowmaApi
from django.conf import settings
from .enums import *
from .forms import *
from core.models import *
from .models import *
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


class Upload(LoginRequiredMixin, TemplateView):
    template_name = 'wowma_upload.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UploadedFileModelForm()
        return context
    def get(self, request, *args, **kwargs):
        if not request.user.wowma_auth:
            messages.error(request, '認証情報が登録されていません')
            return redirect('wowma:dashboard')
        context = self.get_context_data(**kwargs)
        context['pagename'] = 'upload'
        return super().render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = UploadedFileModelForm(request.POST, request.FILES)
        if not form.is_valid():
            context['form'] = form
            return self.render_to_response(context)
        uploaded_file = form.save(commit = True)
        items_to_register = uploaded_file.get_item_objects()
        all_ok = True
        for index, item in enumerate(items_to_register):
            if not item.validate_for_add(index + 1):
                error_record = UploadFileErrorRecord()
                error_record.parent_file = uploaded_file
                error_record.timing = TIMING_VALIDATION
                error_record.line_number = index + 1
                error_record.error_message = item.error
                error_record.save()
                all_ok = False
       
        if not all_ok:
            messages.error(request, 'ファイルにエラーがありました')
            context['errors'] = UploadFileErrorRecord.objects.filter(parent_file = uploaded_file)
            return self.render_to_response(context)
        else:
            # if all ok
            wowma_api = WowmaApi(request.user.wowma_auth)
            for index, item in enumerate(items_to_register):
                if not wowma_api.register_item(item):
                    error_record = UploadFileErrorRecord()
                    error_record.parent_file = uploaded_file
                    error_record.timing = TIMING_RUNTIME
                    error_record.line_number = index + 1
                    error_record.error_message = item.error
                    error_record.save()
                    all_ok = False
            if not all_ok:
                context['errors'] = UploadFileErrorRecord.objects.filter(parent_file = uploaded_file)
                messages.error(request, '登録時にエラーがありました')
                return self.render_to_response(context)
            else:
                messages.success(request, '登録が完了しました')
                return redirect('wowma:upload')
            messages.success(request, '登録が完了しました')
            return redirect('wowma:upload')

            
