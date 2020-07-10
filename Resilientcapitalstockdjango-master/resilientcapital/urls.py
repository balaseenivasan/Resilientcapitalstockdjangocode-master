"""resilientcapital URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url,include
from resilientcapitalapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$',views.index,name='index'),
    url(r'^special/',views.special,name='special'),
    url(r'^resilientcapitalapp/',include('resilientcapitalapp.urls')),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^sp50dma/$', views.plot_view, name='sp50dma'),
    url(r'^sp200dma/$', views.plot_view200dma, name='sp200dma'),
    url(r'^spissues/$', views.plot_spissuesview, name='spissues'),
    url(r'^sprsi70/$', views.plot_sprsi70view, name='sprsi70'),
    url(r'^sprsi30/$', views.plot_sprsi30view, name='sprsi30'),
    url(r'^spupperbolinger/$', views.plot_spupperbolingerview, name='spupperbolinger'),
    url(r'^splowerbolinger/$', views.plot_splowerbolingerview, name='splowerbolinger'),
    url(r'^sp52weekshigh/$', views.plot_sp52weekshighview, name='sp52weekshigh'),
    url(r'^sp52weekslow/$', views.plot_sp52weekslowview, name='sp52weekslow'),
    url(r'^sphighlow/$', views.plot_sphighlowview, name='sphighlow'),
    url(r'^sp24weekshigh/$', views.plot_sp24weekshighview, name='sp24weekshigh'),
    url(r'^sp24weekslow/$', views.plot_sp24weekslowview, name='sp24weekslow'),
    url(r'^spcorrection/$', views.plot_spcorrectionview, name='spcorrection'),
    url(r'^spbearmarket/$', views.plot_spbearmarketview, name='spbearmarket'),
    url(r'^nasdaq50dma/$', views.plot_view50dma, name='nasdaq50dma'),
    url(r'^nasdaq200dma/$', views.plot_nasdaq200dmaview, name='nasdaq200dma'),
    url(r'^nasdaqissues/$', views.plot_nasdaqissuesview, name='nasdaqissues'),
    url(r'^nasdaqrsi70/$', views.plot_nasdaqrsi70view, name='nasdaqrsi70'),
    url(r'^nasdaqrsi30/$', views.plot_nasdaqrsi30view, name='nasdaqrsi30'),
    url(r'^nasdaqupperbolinger/$', views.plot_nasdaqupperbolingerview, name='nasdaqupperbolinger'),
    url(r'^nasdaqlowerbolinger/$', views.plot_nasdaqplowerbolingerview, name='nasdaqlowerbolinger'),
    url(r'^nasdaq52weekshigh/$', views.plot_nasdaq52weekshighview, name='nasdaq52weekshigh'),
    url(r'^nasdaq52weekslow/$', views.plot_nasdaq52weekslowview, name='nasdaq52weekslow'),
    url(r'^nasdaqhighlow/$', views.plot_nasdaqhighlowview, name='nasdaqhighlow'),
    url(r'^nasdaq24weekshigh/$', views.plot_nasdaq24weekshighview, name='nasdaq24weekshigh'),
    url(r'^nasdaq24weekslow/$', views.plot_nasdaq24weekslowview, name='nasdaq24weekslow'),
]
