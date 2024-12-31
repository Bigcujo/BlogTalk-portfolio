from django.shortcuts import render, get_object_or_404, redirect
from .models import GroupChat
from django.contrib.auth.decorators import login_required
from .forms import chatmessageCreateForm

@login_required
def chat_view(request):
    chatgroup = get_object_or_404(GroupChat, group_name="Accounting Group")
    chatmessages = chatgroup.chat_messages.all()[:30]
    form =  chatmessageCreateForm()

    if request.method == "POST":
        form =  chatmessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chatgroup
            message.save()
            context = {
                "message" : message,
                "user" : request.user
            }   
            return render(request, 'chat/partials/chat_message_p.html', context)
    return render(request, "chat/chat.html", {'chatmessages' : chatmessages, 'form': form})