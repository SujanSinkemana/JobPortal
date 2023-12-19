from typing import Any, Dict
from django.contrib import messages 
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render,redirect
from django.views.generic import ListView,DetailView,CreateView
from .pagination import CustomPagination
from django.urls import reverse_lazy
from .models import Job, Category,JobApplication
from .forms import ContactForm
from apps.commons.utils import get_base_url, is_profile_complete
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
# Create your views here.
class HomeView(ListView):
    template_name ='core/home.html'
    pagination_class = CustomPagination
    # queryset = Job.objects.filter(is_active=True)
    
    def get_queryset(self):
        category= self.request.GET.get('category')
        search = self.request.GET.get('search')
        filter_dict = {"is_active":True}
        exclude = dict()
        if self.request.user.is_authenticated:
            exclude.update(job_application__user=self.request.user)
        if category:
            filter_dict.update(category__uuid=category)
        if search:
            filter_dict.update(title__icontains=search)
        print("filterdict...",filter_dict)
        print("exclude...",exclude)
        return Job.objects.filter(**filter_dict).exclude(**exclude).order_by('id') #making filter dynamic
    

    def get_pagination(self):
        # print("get_pagination...",self.pagination_class())
        return self.pagination_class() #obj of CustomPagination
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context ['title']="Home"
        pagination =self.get_pagination() #Gives the object of pagination
        print("pagination...",pagination)
        qs = pagination.get_paginated_qs(views=self) #[job1,job2,job3,job4]
        print("QS...",qs)
        nested_qs = pagination.get_nested_pagination(qs, nested_size=2)
        print("nested_qs...",nested_qs)
        context["job_lists"]= nested_qs
        context['catagories']=Category.objects.all()
        context['base_url']=get_base_url(request=self.request)
        page_number, page_str =pagination.get_current_page(view=self)
        context[page_str]='active'
        context["next_page"]=page_number + 1
        context["prev_page"]=page_number - 1
        if page_number >= pagination.get_last_page(view=self):
            context["next"]="disabled"
        if page_number <= 1:
            context['prev']="disabled"
        context['home_active']='active'
        return context

class JobDetailView(DetailView):
    template_name = "core/job_detail.html"
    queryset =Job.objects.filter(is_active=True)
    slug_field ="uuid" # uuid is the field from database table
    slug_url_kwarg="uuid" # uuid is the value coming from the url
    context_object_name="job"
    print('slug_url_kargs...',slug_url_kwarg)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context=super().get_context_data(**kwargs)
        context['title']="Job Detail"
        return context
    
@login_required   
def job_apply(request, uuid):
    try:
        job = Job.objects.get(uuid=uuid)
    except Job.DoesNotExist:
        messages.error(request,"Something went wrong!")
        return redirect('home')
    if is_profile_complete(request.user):
        JobApplication.objects.get_or_create(user=request.user,job=job,defaults={"status":"APPLIED"})
        messages.success(request,f"You Have Successful Applied for the role{job.title}")
        return redirect('home')
    messages.error(request,"Please Activate Your Account And Complete Your Profile")
    return redirect('home')


@method_decorator(login_required,name='dispatch')
class MyJobsView(ListView):
    template_name = 'core/my_jobs.html'
    context_object_name =  'job_applications'                


    def get_queryset(self) -> QuerySet[Any]:
        status = self.request.GET.get('status')
        filter_dict = {'user':self.request.user}
        if status:
            filter_dict.update(status=status)
        return JobApplication.objects.filter(**filter_dict)
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context=super().get_context_data(**kwargs)
        context['statuses'] = ["APPLIED","SCREENING","SHORTLISTED","REJECTE","SELECTED"]
        return context
    
class ContactView(CreateView):
    template_name ='core/contact.html'
    success_url = reverse_lazy('contact')
    form_class = ContactForm

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        # self.object = None
        form = self.get_form()
        if form.is_valid():
            messages.success(request, "We have Received Your Response")
            # print("self.object..",self.object)
            return self.form_valid(form)
        else:
            self.object= None
            messages.error(request, "Something Went Wrong") 
            # print("self.object..",self.object)          
            return self.form_invalid(form)


    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = "Contact Us"
        context['contact_active'] = "active"
        return context
    