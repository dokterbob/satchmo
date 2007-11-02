from django import template

register = template.Library()
@register.inclusion_tag('_messages.html', takes_context=True)
def show_messages(context):
    messages = context['request'].user.get_and_delete_messages()
    return {'visitor_messages' : messages }
