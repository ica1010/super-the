from django import template

register = template.Library()

@register.filter
def times(number):
    return range(number)



@register.simple_tag(takes_context=True)
def increment_counter(context):
    if 'global_counter' not in context:
        context['global_counter'] = 1
    else:
        context['global_counter'] += 1
    return context['global_counter']