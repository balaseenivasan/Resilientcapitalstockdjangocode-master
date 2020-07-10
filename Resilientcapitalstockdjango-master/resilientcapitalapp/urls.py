from django.conf.urls import url
from django.urls import path
from resilientcapitalapp import views
# SET THE NAMESPACE!
app_name = 'resilientcapitalapp'
# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
    #path('', views.index, name='index'),
    url(r'^register/$',views.register,name='register'),
    url(r'^user_login/$',views.user_login,name='user_login'),
    url(r'^home/$',views.save_datas,name='home'),
    url(r'^sp50dma/$', views.plot_view, name='sp50dma'),

]