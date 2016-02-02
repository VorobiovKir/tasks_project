from django.http import HttpResponseRedirect


def authors_only(function):
    def wrap(request, *args, **kwargs):

        profile = request.user.get_profile()
        if profile.usertype == 'Author':
            return function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
