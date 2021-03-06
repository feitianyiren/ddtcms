﻿# coding=UTF-8
from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from django.template import loader, Context
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from ddtcms.member.countries import CountryField
import datetime
import cPickle as pickle
import base64
import os.path
try:
    from PIL import Image, ImageFilter
except ImportError:
    import Image, ImageFilter

from forum.models import Post
from blog.models import Blog

AVATAR_SIZES = (128, 96, 64, 48, 32, 24, 16)

class UserResumeNotAvailable(Exception):
    pass
    
class UserFavouriteNotAvailable(Exception):
    pass
    
class UserConfigurationNotAvailable(Exception):
    pass




class BaseProfile(models.Model):
    """
    User profile model
    """

    user = models.ForeignKey(User, unique=True)
    date = models.DateTimeField(default=datetime.datetime.now)
    country = CountryField(null=True, blank=True,default="CN")
    latitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True

    def has_avatar(self):
        return Avatar.objects.filter(user=self.user, valid=True).count()

    def __unicode__(self):
        return _("%s's profile") % self.user

    def get_absolute_url(self):
        return reverse("profile_public", args=[self.user])


class Avatar(models.Model):
    """
    Avatar model
    """
    image = models.ImageField(upload_to="upload/member/avatars/%Y/%b/%d")
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True)
    valid = models.BooleanField()

    class Meta:
        unique_together = (('user', 'valid'),)

    def __unicode__(self):
        return _("%s's Avatar") % self.user

    def delete(self):
        base, filename = os.path.split(self.image.path)
        name, extension = os.path.splitext(filename)
        for key in AVATAR_SIZES:
            try:
                os.remove(os.path.join(base, "%s.%s%s" % (name, key, extension)))
            except:
                pass

        super(Avatar, self).delete()

    def save(self):
        for avatar in Avatar.objects.filter(user=self.user, valid=self.valid).exclude(id=self.id):
            base, filename = os.path.split(avatar.image.path)
            name, extension = os.path.splitext(filename)
            for key in AVATAR_SIZES:
                try:
                    os.remove(os.path.join(base, "%s.%s%s" % (name, key, extension)))
                except:
                    pass
            avatar.delete()

        super(Avatar, self).save()


class EmailValidationManager(models.Manager):
    """
    Email validation manager
    """
    def verify(self, key):
        try:
            verify = self.get(key=key)
            if not verify.is_expired():
                verify.user.email = verify.email
                verify.user.save()
                verify.delete()
                return True
            else:
                verify.delete()
                return False
        except:
            return False

    def getuser(self, key):
        try:
            return self.get(key=key).user
        except:
            return False

    def add(self, user, email):
        """
        Add a new validation process entry
        """
        while True:
            key = User.objects.make_random_password(70)
            try:
                EmailValidation.objects.get(key=key)
            except EmailValidation.DoesNotExist:
                self.key = key
                break
        if settings.SEND_REGISTER_MAIL:
            template_body = "member/email/validation.txt"
            template_subject = "member/email/validation_subject.txt"
            site_name, domain = Site.objects.get_current().name, Site.objects.get_current().domain
            body = loader.get_template(template_body).render(Context(locals()))
            subject = loader.get_template(template_subject).render(Context(locals())).strip()
            send_mail(subject=subject, message=body, from_email=None, recipient_list=[email])
        user = User.objects.get(username=str(user))
        self.filter(user=user).delete()
        return self.create(user=user, key=key, email=email)

class EmailValidation(models.Model):
    """
    Email Validation model
    """
    user = models.ForeignKey(User, unique=True)
    email = models.EmailField(blank=True)
    key = models.CharField(max_length=70, unique=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    objects = EmailValidationManager()

    def __unicode__(self):
        return _("Email validation process for %(user)s") % { 'user': self.user }

    def is_expired(self):
        return (datetime.datetime.today() - self.created).days > 0

    def resend(self):
        """
        Resend validation email
        """
        if settings.SEND_REGISTER_MAIL:
            template_body = "member/email/validation.txt"
            template_subject = "member/email/validation_subject.txt"
            site_name, domain = Site.objects.get_current().name, Site.objects.get_current().domain
            key = self.key
            body = loader.get_template(template_body).render(Context(locals()))
            subject = loader.get_template(template_subject).render(Context(locals())).strip()
            send_mail(subject=subject, message=body, from_email=None, recipient_list=[self.email])
        self.created = datetime.datetime.now()
        self.save()
        return True

class UserProfileMediaNotFound(Exception):
    pass


# add by huaitwooos@gmail.com
GENDER_CHOICES = ( ('F', _('Female')), ('M', _('Male')),)
BLOODGROUP_CHOICES= (
    ('A',  _('A TYPE')),
    ('B',  _('B TYPE')),
    ('AB', _('AB TYPE')),
    ('O',  _('O TYPE')),
    ('R',  _('OTHER TYPE')),
    )

ZODIAC_CHOICES=(
    ('RAT',      _('Rat')),
    ('OX',       _('Ox')),
    ('TIGER',    _('Tiger')),
    ('RABBIT',   _('Rabbit')),
    ('DRAGON',   _('Dragon')),
    ('SNAKE',    _('Snake')),
    ('HORSE',    _('Horse')),
    ('GOAT',     _('Goat')),
    ('MONKEY',   _('Monkey')),
    ('ROOSTER',  _('Rooster')),
    ('DOG',      _('Dog')),
    ('PIG',      _('Pig')),
    )

CONSTELLATION_CHOICES=(
    ('ARIES',       _('Aries(the Ram)')),
    ('TAURUS',      _('Taurus(the Bull)')),
    ('GEMINI',      _('Gemini(the Twins)')),
    ('CANCER',      _('Cancer(the Crab)')),
    ('LEO',         _('Leo(the Lion)')),
    ('VIRGO',       _('Virgo(the Virgin)')),
    ('LIBRA',       _('Libra(the Scales)')),
    ('SCORPIO',     _('Scorpio(the Scorpion)')),
    ('SAGITTALIUS', _('Sagittarius(the Archer)')),
    ('CAPRICORNUS', _('Capricornus(the Goat)')),
    ('AQUALIUS',    _('Aquarius(the Water Carrier)')),
    ('PISCES',      _('Pisces(the Fishes)')),
    )

# Create your models here.

		

class ProfileManager(models.Manager):
    """
    Custom manager for the ``RegistrationProfile`` model.
    
    The methods defined here provide shortcuts for account creation
    and activation (including generation and emailing of activation
    keys), and for cleaning out expired inactive accounts.
    
    """
        
    def create_user(self, username, password, email,send_email=settings.REQUIRE_EMAIL_CONFIRMATION):
        """
       ``user``
            The ``User`` to relate the profile to.
        
        """
        new_user = User.objects.create_user(username, email, password)
        new_user.save()        
        profile = self.create_profile(new_user)
        
        return new_user
    
    def create_profile(self, user):
        """
        Create a ``Profile`` for a given ``User``, and return the ``Profile``.
        """

        return self.create(user=user,nickname=user.username,foreigname=user.username)
        

class Profile(BaseProfile):

    firstname      = models.CharField(verbose_name='名字',max_length=255, blank=True)
    surname        = models.CharField(verbose_name='姓氏',max_length=255, blank=True)
    nickname       = models.CharField(verbose_name='昵称',null=True,max_length=20)
    foreigname     = models.CharField(verbose_name='英文名',null=True,max_length=20)
    birthday       = models.DateField(verbose_name='生日',null=True,default=datetime.date.today(), blank=True)
    gender         = models.CharField(verbose_name='性别',null=True,max_length=1, choices=GENDER_CHOICES, blank=True)
    bloodgroup     = models.CharField(verbose_name='血型',null=True,max_length=4, choices=BLOODGROUP_CHOICES,blank=True)
    zodiac         = models.CharField(verbose_name='属相',null=True,max_length=20, choices=ZODIAC_CHOICES,blank=True)
    constellation  = models.CharField(verbose_name='星座',null=True,max_length=20, choices=CONSTELLATION_CHOICES,blank=True)
    height         = models.CharField(verbose_name='身高',null=True,max_length=4,blank=True)
    weight         = models.CharField(verbose_name='体重',null=True,max_length=4,blank=True)
    homeplace      = models.CharField(verbose_name='家乡',null=True,max_length=20,blank=True)
    hobby          = models.CharField(verbose_name='爱好',null=True,max_length=20,blank=True)
    character      = models.CharField(verbose_name='性格',null=True,max_length=20,blank=True)
    profession     = models.CharField(verbose_name='专业',null=True,max_length=20,blank=True)
    career         = models.CharField(verbose_name='职业',null=True,max_length=20,blank=True)
    skills         = models.CharField(verbose_name='技能',null=True,max_length=40,blank=True)    
    webpage        = models.URLField(verbose_name='主页',null=True,blank=True)
    intro          = models.TextField(verbose_name='简短介绍',null=True,max_length=200,blank=True)
    is_public      = models.BooleanField(verbose_name='是否公开',default=True)

    objects = ProfileManager()
    
    def __unicode__(self):
        return self.user.username

    #def get_absolute_url(self):
    #    return "/member/%s/profile" % (self.user.username)
    
    def get_favourite(self):
        """
        Returns user-specific favourite for this user. Raises
        UserFavouriteNotAvailable if this User does not have a  favourite.
        """
        if not hasattr(self, '_favourite_cache'):
            try:
                self._favourite_cache = Favourite._default_manager.get(user__id__exact=self.id)
                self._favourite_cache.user = self
            except (ImportError, ImproperlyConfigured,Favourite.DoesNotExist):
                raise UserFavouriteNotAvailable
        return self._favourite_cache
        
    def get_posts(self):
        return Post.objects.for_user(self.user)

    def total_posts(self):
        try:
            total = self.get_posts().count()
        except AttributeError:
            total = 0
        return total
        
    def get_blogs(self):
        return Blog.objects.for_user(self.user)

    def total_blogs(self):
        try:
            total = self.get_blogs().count()
        except AttributeError:
            total = 0
        return total

    def get_friends(self):
        return Friend.objects.for_user(self.user)

    def total_friends(self):
        try:
            total = self.get_friends().count()
        except AttributeError:
            total = 0
        return total

class Resume(models.Model):
    user          = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    startime      = models.DateField()
    stoptime      = models.DateField()
    event         = models.TextField(max_length=200)

    def __unicode__(self):
        return self.user.username

    def get_absolute_url(self):
        return "/member/%s/resume" % (self.user.username)

#class Education(models.Model):
#    user          = models.ForeignKey(User, unique=True, verbose_name=_('user'))
#    degree        = models.CharField(null=True,max_length=20)
#    school        = models.CharField(null=True,max_length=20)
#    notes         = models.TextField(max_length=200)
#
#    def __unicode__(self):
#        return self.user.username
#
#    def get_absolute_url(self):
#        return "/member/%s/resume" % (self.user.username)


class Favourite(models.Model):
    user          = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    moviestar     = models.CharField(max_length=40)
    movie         = models.CharField(max_length=40)
    sport         = models.CharField(max_length=40)
    scenicspot    = models.CharField(max_length=40)
    singer        = models.CharField(max_length=40)
    song          = models.CharField(max_length=40)
    language      = models.CharField(max_length=40)
    cartoon       = models.CharField(max_length=40)
    clothing      = models.CharField(max_length=40)
    colour        = models.CharField(max_length=40)
    writer        = models.CharField(max_length=40)
    book          = models.CharField(max_length=200)
    season        = models.CharField(max_length=40)
    food          = models.CharField(max_length=40)
    drink         = models.CharField(max_length=40)
    relaxation    = models.CharField(max_length=40)
    recreation    = models.CharField(max_length=40)


    def __unicode__(self):
        return self.user.username

    def get_absolute_url(self):
        return "/member/%s/favourite" % (self.user.username)



class OnlineUser(models.Model):
	"""
	Online users.
	"""
	user         = models.ForeignKey(User)
	visit_page   = models.CharField(_("Location"), max_length=100)
	ip           = models.IPAddressField()
	proxy_ip     = models.IPAddressField()
	browser      = models.CharField(_("Browser"), max_length=100)
	resolution   = models.CharField(_("Resolution of Screen"), max_length=100)
	location     = models.CharField(_("Location"), max_length=100)
	visible      = models.BooleanField(default=True)
	appear       = models.DateTimeField(_("netfault"), blank=True, null=True)
	lastactivity = models.DateTimeField(_("LastActivity"), blank=True, null=True)

	class Meta:
		unique_together = (("user", "ip"),)
		verbose_name = _('OnlineUser')
		verbose_name_plural = _('OnlineUsers')

	def __unicode__(self):
		return u"%s visit %s" % (self.user,self.visit_page)








CONFIG_VALUE_TYPE=(
	("STRING",      _("STRING")),
	("BOOLEAN",     _("BOOLEAN")),
	("INTEGER",     _("INTEGER")),
	("FLOAT",       _("FLOAT")),
	("DATETIME",    _("DATETIME")),
	("OTHER",       _("OTHER")),
	)
class Configuration(models.Model):
    '''
    Represents a userprofile
    '''
    user       = models.ForeignKey(User,unique=True)
    model      = models.CharField(max_length=20,blank=True)
    key        = models.CharField(max_length=20,blank=True)
    value      = models.CharField(max_length=20,blank=True)
    value_type = models.IntegerField(blank=True,choices=CONFIG_VALUE_TYPE,default=0)
    posts = models.IntegerField(blank=True,default=0)
    homepage = models.CharField(max_length=500,blank=True,default=u'')
    description = models.TextField(blank=True,default=u'')
    rank = models.IntegerField(blank=True,default=0)
    last_activedate = models.IntegerField('最后操作时间',default=0,editable=False)
    is_online = models.BooleanField(u'是否在线',blank=True)
    
    def __unicode__(self):
        return self.user.username


class FriendManager(models.Manager):
    def for_user(self, user):
        user_friends = Q(friend__exact=user)
        return self.filter(user_friends)



class Friend(models.Model):
    friend     = models.ForeignKey(User)
    nickname   = models.CharField(max_length=40,null=True,blank=True)
    notes      = models.CharField(max_length=40,null=True,blank=True)

    class Meta:
        ordering     = ('friend',)
        verbose_name = _('Friend')
        verbose_name_plural = _('Friends')

    def __unicode__(self):
        return self.friend.fullname()

    def get_absolute_url(self):
        return "/member/friends/%d/" % (self.id)


class Regiment(models.Manager):
    """
    My colonel and my regiment.TuanGroup
    """
    title          = models.CharField(_('title'), max_length=50)
    slug           = models.SlugField(max_length=50,help_text='alias to the name,use english')
    colonel        = models.ForeignKey(User,related_name='colonels')
    description    = models.CharField(_('description'),blank=True,null=True,max_length=200)
    members        = models.ManyToManyField(User, blank=True)
    pub_time       = models.DateTimeField(_("pub_time"), blank=True, null=True,default=datetime.datetime.now())
    lastactivity   = models.DateTimeField(_("LastActivity"), blank=True, null=True,default=datetime.datetime.now())

    class Meta:
       ordering      = ('title','-lastactivity',)
       verbose_name = _('Regiment')
       verbose_name_plural = _('Regiments')

    def __unicode__(self):
       return self.title

    def get_absolute_url(self):
       return "regiment/%s/" % self.slug

    def save(self,*args,**kwargs):
        if not self.slug:
           self.slug = slugify(self.title)
           self.slug = self.slug.lower().replace('-','_')
        super(Regiment,self).save(*args,**kwargs)