# -*- coding: utf-8 -*-
#python.
from datetime import datetime
import urllib

#django.
from django.shortcuts import get_object_or_404, render_to_response
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden

from django.template import RequestContext


from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list
from django.views.generic.list_detail import object_detail

from django.contrib.auth.decorators import login_required

#3dpart.


#ddtcms.
from models import Link,Category
from forms  import CreateLinkForm,CGPUploadForm

def index(request):
    qs = Link.objects.all()
    if not request.user.is_authenticated():
        user_category = None
    else:
		user_category = Category.objects.select_related().filter(user = request.user,parent__isnull=True)
    
    return object_list(request,
                       qs,
                       template_object_name='link',
                       paginate_by=30,
                       extra_context={'user_category':user_category})


#@login_required
def link_create(request):
	"""
	Rudimentary post function - this should probably use 
	newforms, although not sure how that goes when we're updating 
	two models.

	Only allows a user to post if they're logged in.
	"""
	if not request.user.is_authenticated():
		return HttpResponseForbidden('hhhh')

	if request.method == 'POST':
		form = CreateLinkForm(request.POST)
		if form.is_valid():
			linktitle =form.cleaned_data['title']            
			url       =form.cleaned_data['url']    
			desc      =form.cleaned_data['description']
			s = Link(title=linktitle,url=url,notes=desc)
			s.save()
			
			#return HttpResponseRedirect(s.get_absolute_url())
			return HttpResponseRedirect("/link/")
	else:
		
		#t=urllib.unquote(request.GET.get('t', 'title not set')).decode('utf8')
		#t=urllib.unquote(request.GET.get('t', 'title not set'))
		t=request.GET.get('t', 'title not set')
		u=request.GET.get('u', 'url not set')
		c=request.GET.get('c', 'title not set')

		form = CreateLinkForm(initial={ 'title': t,
										'url': u,
										'description': c
									})

	msg=request.method
	return render_to_response('link/newlink.html',
		RequestContext(request, {
			'form': form,
			'msg':msg,
		}))


def link_detail(request,object_id):
    qs = Link.objects.all()
    object_id=int(object_id)
    try:
        link=Link.objects.all().get(id=object_id)
    except Link.DoesNotExist:
        raise Http404
    
    try:
        userinfo=link.link_users.all().latest("start_date")
    except UserInfo.DoesNotExist:
        userinfo = None
    
    return object_detail(request,
                       qs,
                       object_id=object_id,
                       template_object_name='link',
                       extra_context={'userinfo':userinfo,})

def link_change(request,object_id):
    return HttpResponse("Under construction")

def link_delete(request,object_id):
    return HttpResponse("Under construction")

def link_import(request):
	"""
	Rudimentary post function - this should probably use 
	newforms, although not sure how that goes when we're updating 
	two models.

	Only allows a user to post if they're logged in.
	"""
	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	if request.method == 'POST':
		form = CGPUploadForm(request.POST)
		if form.is_valid():
			linktitle =form.cleaned_data['title']            
			url       =form.cleaned_data['url']    
			desc      =form.cleaned_data['description']
			s = Link(title=linktitle,url=url,notes=desc)
			s.save()
			
			#return HttpResponseRedirect(s.get_absolute_url())
			return HttpResponseRedirect("/link/")
	else:
		
		#t=urllib.unquote(request.GET.get('t', 'title not set')).decode('utf8')
		#t=urllib.unquote(request.GET.get('t', 'title not set'))
		t=request.GET.get('t', 'title not set')
		u=request.GET.get('u', 'url not set')
		c=request.GET.get('c', 'title not set')

		form = CreateLinkForm(initial={ 'title': t,
										'url': u,
										'description': c
									})

	msg=request.method
	return render_to_response('link/newlink.html',
		RequestContext(request, {
			'form': form,
			'msg':msg,
		}))


def link_export(request):
	"""
	Rudimentary post function - this should probably use 
	newforms, although not sure how that goes when we're updating 
	two models.

	Only allows a user to post if they're logged in.
	"""
	if not request.user.is_authenticated():
		#return HttpResponseServerError()
		return HttpResponseForbidden()

	if request.method == 'POST':
		form = CreateLinkForm(request.POST)
		if form.is_valid():
			linktitle =form.cleaned_data['title']            
			url       =form.cleaned_data['url']    
			desc      =form.cleaned_data['description']
			s = Link(title=linktitle,url=url,notes=desc)
			s.save()
			
			#return HttpResponseRedirect(s.get_absolute_url())
			return HttpResponseRedirect("/link/")
	else:
		
		#t=urllib.unquote(request.GET.get('t', 'title not set')).decode('utf8')
		#t=urllib.unquote(request.GET.get('t', 'title not set'))
		t=request.GET.get('t', 'title not set')
		u=request.GET.get('u', 'url not set')
		c=request.GET.get('c', 'title not set')

		form = CreateLinkForm(initial={ 'title': t,
										'url': u,
										'description': c
									})

	msg=request.method
	return render_to_response('link/newlink.html',
		RequestContext(request, {
			'form': form,
			'msg':msg,
		}))