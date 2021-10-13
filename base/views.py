from django.shortcuts import render, redirect
# 장고에서는 미리 만들어놓은 generic 뷰 == 클래스형 뷰
# (해당 테이블(모델)에 필요한 컬럼들의 입력 form을 자동으로 생성해서 보여줌)
# ==> 웹페이지 접속 -> 페이지 확인
# ==> URL 입력 -> 웹 서버가 뷰 찾아서 동작시킴 -> 응답
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView # 로그인, 로그아웃 뷰
from django.contrib.auth.mixins import LoginRequiredMixin # 로그인 권한 지정
from django.contrib.auth.forms import UserCreationForm #가입폼
from django.contrib.auth import login # 로그인

from .models import Task


class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')
        # urls.py가 로딩되어 있는지 확인 (좀 더 천천히 확인) / (reverse 사용해도 무방)


class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        # *args == arguments (여러 개의 인자를 받고 싶을 때) // 언팩킹
        # **kwargs == 딕셔너리 형태 (key, value를 함수식에 넘겨줄 때 사용) // 언팩킹
        if self.request.user.is_authenticated: # 유저 로그인 여부 확인(로그인 상태면 True)
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)






class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            # filter(title__icontains=search_input) : 해당문자 포함하는 모든 결과물
            #               startswith              : 해당문자로 시작하는 모든 결과물
            context['tasks'] = context['tasks'].filter(
                title__startswith=search_input)

        context['search_input'] = search_input

        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks') # template에서 전송 마친 후, redirect하는 곳

    def form_valid(self, form):  # user가 들어가지 않는 문제 해결해줌
        form.instance.user = self.request.user
        # form 유저는 request를 주는 유저를 가지고 스스로 리턴 --> 전송하는 form은 user를 가져갈 수 O
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')


class DeleteView(DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')

