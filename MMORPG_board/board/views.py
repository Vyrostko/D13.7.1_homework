from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import *
from django.template.loader import render_to_string
from django.urls import reverse
from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django import forms
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from decouple import config

class AdsList(ListView): # Все объявления
    model = Ad
    template_name = 'board/ads.html'
    context_object_name = 'ads'
    ordering = ['-dateCreation']
    paginate_by = 10

class MyAdsList(LoginRequiredMixin, ListView): # Мои объявления
    model = Ad
    template_name = 'board/my_ads.html'
    context_object_name = 'ads'
    paginate_by = 10

    def get_queryset(self): # Для того, чтобы на странице личных объявлений показывались только объявления, созданные самим пользователем
        return Ad.objects.filter(author=self.request.user.id).order_by('-dateCreation')

class AdsDetailView(DetailView): # Показ конкретного объявления
    model = Ad
    template_name = 'board/ad.html'
    context_object_name = 'ad'
    queryset = Ad.objects.all()

class AdsCreateView(LoginRequiredMixin, CreateView): # Создание объявления
    form_class = AdsForm
    template_name = 'board/ad_create.html'

    def form_valid(self, form):
        # Устанавливаем автора объявления в текущего пользователя
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('ad', kwargs={'pk': self.object.pk})

class AdsUpdateView(LoginRequiredMixin, UpdateView): # Редактирование объявления
    form_class = AdsForm
    template_name = 'board/ad_create.html'

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Ad.objects.get(pk=id)

    def get_success_url(self):
        return reverse('ad', kwargs={'pk': self.object.pk})

class AdsDeleteView(LoginRequiredMixin, DeleteView): # Удаление объявления
   template_name = 'board/ad_delete.html'
   queryset = Ad.objects.all()
   success_url = '/ads/'

class CommentCreateView(LoginRequiredMixin, CreateView): # Создание отклика
    model = Comment
    form_class = CommentForm
    template_name = 'board/comment_create.html'

    def form_valid(self, form):
        ad_id = self.kwargs['pk']
        ad = Ad.objects.get(pk=ad_id)
        comment = form.save(commit=False)
        comment.commentAuthor = self.request.user
        comment.save()
        ad.comments.add(comment)
        comment_text = form.cleaned_data['text']
        ad_owner_email = ad.author.email

        html_content = render_to_string(
            'board/new_comment_email.html',
            {
                'comment_text': comment_text,
                'ad': ad,
                'comment_author': comment.commentAuthor,
            }
        )

        msg = EmailMultiAlternatives(
            subject=f"Отклик на ваше объявление '{ad.title}'",
            body=f"Здравствуйте!\n\nНа ваше объявление поступил новый отклик от пользователя {comment.commentAuthor}",
            from_email=config('DEFAULT_FROM_EMAIL'),
            to=[ad_owner_email],
        )
        msg.attach_alternative(html_content, "text/html")  # добавляем html
        msg.send()  # отсылаем
        # print(html_content)

        return super().form_valid(form)

    def get_success_url(self):
        ad_id = self.kwargs['pk']
        ad = Ad.objects.get(pk=ad_id)
        return reverse('ad', kwargs={'pk': ad.id})

class CommentsOnMyAdsList(LoginRequiredMixin, ListView): # представление, для отображения откликов, котороые оставили другие пользователи на мои объявления
    model = Ad
    template_name = 'board/comments_on_my_ads.html'
    context_object_name = 'ads'
    paginate_by = 10

    def get_queryset(self):
        return Ad.objects.filter(author=self.request.user.id).order_by('-dateCreation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ads_with_comments = []
        for ad in context['ads']:
            if ad.comments.exists():  # Проверка наличия комментариев у объявления
                ads_with_comments.append(ad)

        context['ads_with_comments'] = ads_with_comments

        # для фильтрации откликов по объявлениям
        selected_ad_id = self.request.GET.get('selected_ad')
        if selected_ad_id:
            selected_ad = Ad.objects.get(id=selected_ad_id)
            context['selected_ad'] = selected_ad

            comments_for_selected_ad = selected_ad.comments.all()
            context['comments_for_selected_ad'] = comments_for_selected_ad

        return context

def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('comments_on_my_ads')

def accept_comment(request, pk): # Принятие откликов
    comment = get_object_or_404(Comment, pk=pk) # Получаем отклик
    ad = comment.ads_comments.first()  # Получаем объявление, к которому относится отклик
    author_of_ad = ad.author  # Получаем автора объявления
    author_of_comment = comment.commentAuthor
    context = {
        'author_of_ad': author_of_ad,
        'ad': ad,
        'author_of_comment': author_of_comment
    }
    template_name = 'board/accept_comment_email.html'

    html_content = render_to_string(template_name, context)
    msg = EmailMultiAlternatives(
        subject=f"Здравствуйте {author_of_comment}!",
        body=f"{author_of_ad} принял ваш отклик на объявление { ad.title }</a>",
        from_email=config('DEFAULT_FROM_EMAIL'),
        to=[comment.commentAuthor.email],
    )
    msg.attach_alternative(html_content, "text/html")  # добавляем html
    msg.send()
    # print(html_content)

    comment.delete()
    return redirect('comments_on_my_ads')