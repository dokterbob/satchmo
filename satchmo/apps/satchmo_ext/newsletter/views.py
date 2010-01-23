from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _, ugettext
from satchmo_ext.newsletter.forms import NewsletterForm

def add_subscription(request, template="newsletter/subscribe_form.html", 
    result_template="newsletter/update_results.html", form=NewsletterForm):
    """Add a subscription and return the results in the requested template."""

    return _update(request, True, template, result_template, form=form)

def remove_subscription(request, template="newsletter/unsubscribe_form.html",
    result_template="newsletter/update_results.html", form=NewsletterForm):
    """Remove a subscription and return the results in the requested template."""

    return _update(request, False, template, result_template, form=form)

def update_subscription(request, template="newsletter/update_form.html", 
    result_template="newsletter/update_results.html", form=NewsletterForm):
    """Add a subscription and return the results in the requested template."""

    return _update(request, 'FORM', template, result_template, form=form)

def _update(request, state, template, result_template, form=NewsletterForm):
    """Add a subscription and return the results in the requested template."""
    success = False
    result = ""

    if request.method == "POST":
        workform = form(request.POST)
        if workform.is_valid():
            if state == 'FORM':
                # save with subcription status from form
                result = workform.save()
            else:
                # save with subscription status explicitly set
                result = workform.save(state)
            success = True
        else:
            result = ugettext('Error, not valid.')

    else:
        workform = form()

    ctx = RequestContext(request, {
        'result' : result,
        'form' : workform
    })

    if success:
        return render_to_response(result_template, context_instance=ctx)
    else:
        return render_to_response(template, context_instance=ctx)
