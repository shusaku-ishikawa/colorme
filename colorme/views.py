from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView, ListView
from django.conf import settings
from .models import *
from core.models import User
from .enums import *
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
import csv
from io import TextIOWrapper, StringIO
from .forms import *
from django.core.management import call_command
from .delayed_jobs import execute_job_by_user

class DashBoard(LoginRequiredMixin, TemplateView):
    template_name = 'colorme_dashboard.html'
class Jobs(LoginRequiredMixin, TemplateView):
    template_name = 'colorme_jobs.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagename'] = 'colorme_job'
        context['job_list'] = Job.objects.filter(user = self.request.user).order_by('-pk')[:5]
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        job_name = request.POST.get('job_name')
        job = Job(user = request.user, job_name = job_name)
        job.save()
        
        execute_job_by_user(job.id)
        messages.success(request, f'JOB {job_name}を登録しました。')
        return redirect('colorme:job')
class Search(LoginRequiredMixin, ListView):
    template_name = 'colorme_searchitems.html'
    model = Item
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagename'] = 'colorme_search'
        context['q'] = kwargs['q']
        return context

    def get_queryset(self, **kwargs):
        self.queryset = self.model.objects.filter(user = self.request.user)
        if kwargs['q']:
            self.queryset = self.queryset.filter(item_name__icontains = kwargs['q'])
        queryset = super().get_queryset()
        return queryset

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
    template_name = 'colorme_delete.html'
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
        items_to_delete = request.POST.getlist('items_to_delete[]')
        for item_id in items_to_delete:
            item = Item.objects.get(item_id = item_id)
            item.delete()
            messages.success(request, f'{item.item_id}を削除しました')
        return redirect('colorme:search')

class Upload(LoginRequiredMixin, TemplateView):
    template_name = 'colorme_upload.html'
    max_display = 5

    def get_queryset(self, **kwargs):
        queryset = UploadFile.objects.filter(user = self.request.user).order_by('-pk')
        if len(queryset) > self.max_display:
            print(type(queryset[0:5]))
            return queryset[0:5]
        else:
            return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagename'] = 'colorme_upload'
        context['form'] = UploadFileModelForm()
        context['uploaded_files'] = self.get_queryset()
        return context

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = UploadFileModelForm(request.POST, request.FILES)
        if not form.is_valid():
            context['form'] = form
            return self.render_to_response(context)
        uploaded_file = form.save(commit = True)
        messages.success(request, '登録が完了しました。コマンドで取り込みを実行してください。')
        return redirect('colorme:upload')

def process_uploaded_file(request):
    if request.method == 'POST':
        target_file_id = request.POST.get('file_id')
        call_command('import_csv', request.user.username, file=target_file_id)
        
        target_file = UploadFile.objects.get(id = target_file_id)
        if target_file.errors.all():
            messages.error(request, '登録時にエラーがありました')
        else:
            messages.success(request, '登録が完了しました')
        return redirect('colorme:upload')
    else:
        print('get called')
            
