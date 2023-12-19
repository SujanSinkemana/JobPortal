from typing import Any, Dict
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView,CreateView
from .forms import UserRegistrationForm, UserloginForm, UserProfileForm
from django.urls import reverse_lazy
from django.contrib import messages
from apps.commons.utils import validate_email, authenticate_user, is_profile_complete
from django.contrib.auth import login, logout
from apps.commons.decorators import redirect_to_home_if_authenticated
from django.utils.decorators import method_decorator
from .utils import send_email_activation_mail
from django.contrib.auth import get_user_model
from .models import UserAccountActivationKey
from django.contrib.auth.decorators import login_required
from .models import UserProfile
User = get_user_model()

# Create your views here.
@method_decorator(redirect_to_home_if_authenticated,name='get')
class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name ='account/registration.html'
    success_url = reverse_lazy('home')

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title']="signup"
        return context

    def post(self,request,*arg, **kwargs):
        self.object = None
        form = self.get_form()
        
        if form.is_valid():
            messages.success(request,'An Activation Email Has Been Sent To You!')
            response = self.form_valid(form) #yo thau ma user create hunxa
            print('response...',response)
            user = self.object
            print('user...',user)
            send_email_activation_mail(request,user)
            return response
        else:
            return self.form_invalid(form)
        
class UserloginView(CreateView):
    template_name = 'account/login.html'
    success_url= reverse_lazy('home')
    form = UserloginForm

    @redirect_to_home_if_authenticated
    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        return render(request,self.template_name,context={"title":"login","form":self.form()})
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        form = self.form(request.POST)
        print("form...",form)
        username_or_email = request.POST['username_or_email']
        password = request.POST['password']
        if validate_email(username_or_email):
            user = authenticate_user(password,email=username_or_email)
        else:
            user = authenticate_user(password,username=username_or_email)
        if user is not None:
            login(request, user)
            messages.success(request,"user login is Done")
            return redirect('home')
        messages.error(request,"Invalid Username or Password")
        return redirect('user_login')
    
def user_logout(request):
    logout(request)
    messages.success(request, 'User logout')
    return redirect('home')

def user_account_activation(request, username,key):
    if UserAccountActivationKey.objects.filter(user__username=username,key=key):
        User.objects.filter(username=username).update(account_activate=True)
        UserAccountActivationKey.objects.filter(user__username=username).delete()
        messages.success(request,"Your Account had been activated")
        
    else:
        messages.error(request, "Invalid Link")
    return redirect('user_register')
    
@method_decorator(login_required, name="dispatch")
class UserProfileView(TemplateView):
    template_name ='account/user_profile.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title']='User Profile'
        context['is_profile_complete'] = is_profile_complete(self.request.user)
        return context
    
@method_decorator(login_required, name="dispatch")    
class UserProfileUpdateView(CreateView):
    template_name = "account/user_profile_update.html"
    form_class = UserProfileForm
    success_url =reverse_lazy('user_profile')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title']= "Profile Update"
        return context
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.object = None
        form = self.get_form()
        
        if form.is_valid():
           resume = form.cleaned_data.pop('resume', None)
           pp = form.cleaned_data.pop('profile_picture',None)
           up,_ = UserProfile.objects.update_or_create(user=self.request.user,defaults=form.cleaned_data)
           if resume or pp:
            if resume:
                up.resume = resume
            if pp:
                up.profile_picture = pp
            up.save()
            messages.success(request,"Your Profile has beem Updated")
            return redirect('user_profile')
        else:
           error_dict = form.error.get_json_data()
           error_dict_values = list(error_dict.values())
           error_message = error_dict_values[0][0].get("message")
           messages.error(request, error_message)
           #messages.error(request, "form.error")
           return self.form_invalid(form)
           