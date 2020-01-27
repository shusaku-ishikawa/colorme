from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView
from .thebase_api import thebase_api
from django.conf import settings
from .models import *
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
        context['pagename'] = 'dashboard'
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
        context['pagename'] = 'authorize'
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

class Search(LoginRequiredMixin, TemplateView):
    template_name = 'thebase_searchitems.html'
    def get(self, request, *args, **kwargs):
        if not request.user.thebase_auth or not request.user.thebase_auth.access_token:
            messages.error(request, 'アクセストークンが発行されていません')
            return redirect('thebase:dashboard')
        context = self.get_context_data(**kwargs)
        context['pagename'] = 'search'
        if 'action' in request.GET and request.GET.get('action') == 'search': 
            if 'q' in request.session:
                del request.session['q']
            q = request.GET.get('q') or ''
            request.session['q'] = q
        else:
            q = request.session['q'] if 'q' in request.session else None
        context['q'] =  q        
        context['search_result'] = thebase_api.search_items(request.user.thebase_auth, q)
        print(context["search_result"])
        return self.render_to_response(context)
class Delete(LoginRequiredMixin, TemplateView):
    template_name = 'thebase_delete.html'
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        operation = request.GET.get('operation')
        selected_items = request.GET.getlist('selected_items[]')
        context['items_to_delete'] = selected_items
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        items_to_delete = request.POST.getlist('items_to_delete[]')
        for item_id in items_to_delete:
            item  = Item(item_id)
            if not item.delete(request.user.thebase_auth):
                messages.error(request, item.error)
                print(item.error)
            else: # if success
                print('item successfully deleted')
                messages.success(request, f'{item.item_id}を削除しました')
        return redirect('thebase:search')

class Upload(LoginRequiredMixin, TemplateView):
    template_name = 'thebase_upload.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UploadedFileModelForm()
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.thebase_auth or not request.user.thebase_auth.access_token:
            messages.error(request, 'アクセストークンが発行されていません')
            return redirect('thebase:dashboard')
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
            for item in items_to_register:
                if item.valid:
                    if not item.item_id: # if new
                        if not item.add(request.user.thebase_auth):
                            error_record = UploadFileErrorRecord()
                            error_record.parent_file = uploaded_file
                            error_record.timing = TIMING_RUNTIME
                            error_record.line_number = item.line_number
                            error_record.error_message = item.error
                            error_record.save()
                            all_ok = False
                    else: # if edit
                        if not item.edit(request.user.thebase_auth):
                            error_record = UploadFileErrorRecord()
                            error_record.parent_file = uploaded_file
                            error_record.timing = TIMING_RUNTIME
                            error_record.line_number = item.line_number
                            error_record.error_message = item.error
                            error_record.save()
                            all_ok = False
            if not all_ok:
                messages.error(request, '登録時にエラーがありました')
                context['errors'] = UploadFileErrorRecord.objects.filter(parent_file = uploaded_file)
                return self.render_to_response(context)
            else:
                messages.success(request, '登録が完了しました')
                return redirect('thebase:upload')

            
