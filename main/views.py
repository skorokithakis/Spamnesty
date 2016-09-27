from annoying.decorators import render_to

#from .models import Conversation


@render_to("home.html")
def home(request):
    return {}
