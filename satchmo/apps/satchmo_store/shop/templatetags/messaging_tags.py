from django import template

register = template.Library()

def show_messages(context):
    messages = context['request'].user.get_and_delete_messages()
    return {'visitor_messages' : messages }

register.inclusion_tag('shop/_messages.html', takes_context=True)(show_messages)
