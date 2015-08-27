from five import grok
from plone.directives import dexterity, form

from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from plone.autoform.interfaces import IFormFieldProvider
from zope.interface import alsoProvides

from zope.interface import invariant, Invalid

from z3c.form import group, field

from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile

from plone.app.textfield import RichText

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder
#from plone.multilingualbehavior.directives import languageindependent
from collective import dexteritytextindexer

from wccpilgrimagesite.app import MessageFactory as _
from zope.app.container.interfaces import IObjectAddedEvent
from Products.CMFCore.utils import getToolByName
from plone.app.dexterity.behaviors.exclfromnav import IExcludeFromNavigation
from plone.i18n.normalizer import idnormalizer
import datetime


from zope.interface import invariant, Invalid
import re
# Interface class; used to define content-type schema.
from wccpilgrimagesite.app import utils

from zope.schema import ValidationError
from Products.CMFDefault.utils import checkEmailAddress
from Products.CMFDefault.exceptions import EmailAddressInvalid
from zope.schema.interfaces import RequiredMissing
from zope.app.container.interfaces import IObjectAddedEvent

class InvalidEmailAddress(ValidationError):
    "Invalid email address"

def validateaddress(value):
    try:
        checkEmailAddress(value)
    except EmailAddressInvalid:
        raise InvalidEmailAddress(value)
    return True

class IUserComment(form.Schema, IImageScaleTraversable):
    """
    User Comment
    """

    title = schema.TextLine(
        title=u'Name',
        required=True,
    )

    email = schema.TextLine(
        title=u'E-mail',
        required=True,
        constraint=validateaddress,
    )

    message = schema.Text(
        title=u'Message',
        required=True,
    )

    # datetime_added = schema.Datetime(
    #     title=u'Datetime added',
    #     required=True,
    # )

    image = NamedBlobImage(
        title=u'Image',
        required=False,
    )

    form.mode(votes_count='hidden')
    votes_count = schema.Int(
        title=u'Current votes count',
        required=False,
        default=0
    )

#    comment_in_steps = RelationList(
#        title=u'Pilgrimage step',
#        default=[],
#        value_type=RelationChoice(
#            source=ObjPathSourceBinder(
#                path={'query': '/en/pilgrimage-steps'},
#            ),
#        ),
#        required=False,
#    )

    # @invariant
    # def addressInvariant(data):
    #     if not re.match("[^@]+@[^@]+\.[^@]+", data.email):
    #         raise Invalid(_(u"Invalid email!"))
    # pass

alsoProvides(IUserComment, IFormFieldProvider)



# @grok.subscribe(IUserComment, IObjectAddedEvent)
# def _createObject(context, event):
#     parent = context.aq_parent
#     id = context.getId()
#     object_Ids = []
#     catalog = getToolByName(context, 'portal_catalog')
#     path = '/'.join(parent.getPhysicalPath())
#     brains = catalog.unrestrictedSearchResults(path={'query':path, 'depth':1}, portal_type='wccpilgrimagesite.app.usercomment')
#     for brain in brains:
#         object_Ids.append(brain.id)
    
#     temp_new_id = str(idnormalizer.normalize(context.title))
#     new_id = temp_new_id.replace("-","")
#     test = ''
#     if new_id in object_Ids:
#         test = filter(lambda name: new_id in name, object_Ids)
#         if len(test) > 1:
#             test = filter(lambda name: new_id+'-' in name, object_Ids)
#         if '-' not in (max(test)):
#             new_id = new_id + '-1'
#         if '-' in (max(test)):
#             new_id = new_id +'-' +str(int(max(test).split('-')[-1])+1) 

#     parent.manage_renameObject(id, new_id )
#     context.setTitle(context.title)

#     #exclude from navigation code
#     # behavior = IExcludeFromNavigation(context)
#     # behavior.exclude_from_nav = True

#     context.reindexObject()
#     return

# @form.default_value(field=IUserComment['datetime_added'])
# def currentDate(self):
#     return datetime.datetime.today()


@form.error_message(field=IUserComment['title'], error=RequiredMissing)
def nameOmittedErrorMessage(value):
    return _(u"No name provided.")

@form.error_message(field=IUserComment['message'], error=RequiredMissing)
def nameOmittedErrorMessage(value):
    return _(u"No message provided.")

@form.error_message(field=IUserComment['email'], error=RequiredMissing)
def nameOmittedErrorMessage(value):
    return _(u"No email provided.")

@grok.subscribe(IUserComment, IObjectAddedEvent)
def _createObject(context, event):
    mailhost = getToolByName(context, 'MailHost')
    email = ''
    message = ''
    image = ''
    
    if context.image:
        image = context.image.filename
    if context.message:
        message = context.message
    if context.email:
        email = context.email
    
    mSubj = "A New Comment Has Been Added"
    mFrom = 'pilgrimage@wcc-coe.org'
    mTo = 'afterfive2015@gmail.com, pilgrimage@wcc-coe.org'
    
    
    
    mBody = "A site visitor has just commented. Below are the details of the comment.\n"
    mBody += "\n"
    mBody += "Name: "+context.title+"\n"
    mBody += "Email: "+email+"\n"
    mBody += "Message: "+message+"\n"
    
    mBody += "\n"
    mBody += "To review the above pledge, visit:\n"
    mBody += "\n"
    mBody += context.absolute_url()+"\n"
    mBody += "\n"
    mBody += context.absolute_url()+"/content_status_modify?workflow_action=publish\n"
    mBody += "\n"
    
    mBody += "Thank you.\n\n"
    mBody += "----------\n"
    mBody += "WCC Pilgrimage\n"
    mBody += "pilgrimage@wcc-coe.org\n"
    mBody += "http://wccpilgrimage.org\n"
    try:
        mailhost.send(mBody, mto=mTo, mfrom=mFrom, subject=mSubj, immediate=True, charset='utf8', msg_type=None)
    except Exception, e:
        context.plone_utils.addPortalMessage(u'Unable to send email', 'info')
        return None
