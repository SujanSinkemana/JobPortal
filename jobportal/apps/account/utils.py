from apps.commons.utils import get_base_url, get_random_key
from .models import UserAccountActivationKey

def send_email_activation_mail(request,user):
    key = get_random_key(50)
    base_url =get_base_url(request)
    activation_url ="".join([base_url,'account/activate/', f'{user.username}/', f'{key}/'])
    subject = "Account Activation"
    message =f"""
    hellow, {user.get_full_name}. Please Click the provided link to activate your account.
    {activation_url}
    """
    from_email ="jpt@jpt.com"
    user.email_user(subject=subject,message=message,from_email=from_email)
    UserAccountActivationKey.objects.create(user=user, key=key)