from .forms import CreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy

class SignupView(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'



