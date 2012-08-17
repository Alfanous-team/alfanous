# Create your views here.


from django.http import HttpResponse
from django.shortcuts import render_to_response
import datetime

from django.utils import translation
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.utils.translation import pgettext_lazy # for ambiguities
from django.utils.translation import get_language_info







def results(request):

    # language information
    language = translation.get_language_from_request(request)
    language_info = get_language_info(language)

    #print  language ,language_info['name'], language_info['name_local'], language_info['bidi']
     

    translation.activate(language)
    request.LANGUAGE_CODE = translation.get_language()
    

    return render_to_response('wui.html', {"bidi": "rtl" if language_info['bidi'] else "ltr","language_local_name": language_info['name_local']})
