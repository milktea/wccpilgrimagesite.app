from five import grok
from plone.directives import dexterity, form
from Products.CMFCore.interfaces import IContentish
from plone import api
import json
from wccpilgrimagesite.app.content.pilgrimage_steps import IPilgrimageSteps
import base64
from plone.dexterity.utils import createContentInContainer, createContent
from plone import namedfile
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.utils import getToolByName
from plone.i18n.normalizer import idnormalizer

grok.templatedir('templates')

def is_number(s):
    try:
        float(s)
        return True
    except Exception:
        return False

class api_add_usercomment(grok.View):
    grok.context(IPilgrimageSteps)
    grok.require('zope2.View')
    grok.name('add+usercomment')
    
    def __call__(self):
        request = self.request
        context = self.context
        title = ''
        email = ''
        message = ''
        iamge = ''
        parent_path = '/'.join(context.getPhysicalPath())
        if request.form:
            form = request.form
            if 'title' in form:
                item = createContentInContainer(context, 'wccpilgrimagesite.app.usercomment', checkConstraints=False, title=u"User Comment")
                setattr(item, 'title', "User Comment")
                item.title = form['title']
                title = form['title']
                if 'email' in form:
                    item.email = form['email']
                    email = form['email']
                    
                if 'message' in form:
                    item.message = form['message']
                    message = form['message']

                if 'image' in form:
                    item.image = namedfile.NamedBlobFile(
                        base64.b64decode(form['docData'].split(';base64,')[1]),
                        filename = form['docName'].decode('utf-8', 'ignore')
                    )

                object_Ids = []
                catalog = getToolByName(context, 'portal_catalog')
               
                brains = catalog.unrestrictedSearchResults(path={'query':parent_path, 'depth':1}, portal_type='wccpilgrimagesite.app.usercomment')
                for brain in brains:
                    object_Ids.append(brain.id)
                id = str(idnormalizer.normalize(item.title))
                if id in object_Ids:
                    test = filter(lambda name: id in name, object_Ids)
                    id = id +'-'+str(len(test))
                context.manage_renameObject(item.id, id)
                item.reindexObject()

        return self._response(response={'mssg': 'Thank you for your contribution! It will appear on the website after it has been approved by one of our staff members.'})
    
    def _response(self, response={}, status_code=200, status_message=''):
        view_response = self.request.response
        view_response.setHeader('Content-type', 'application/json')
        view_response.setStatus(status_code, status_message)
        view_response.setBody(json.dumps(response), lock=True)

        return view_response
    
