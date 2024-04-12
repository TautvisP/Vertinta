from django import template

register = template.Library()


@register.simple_tag
def match_value(actual_value, expected_value, match_result, miss_result):
    return match_result if actual_value == expected_value else miss_result


@register.simple_tag(takes_context=True)
def match_url(context, expected_value, match_result, miss_result=''):
    return match_value(context.request.resolver_match.url_name, expected_value, match_result, miss_result)


@register.simple_tag(takes_context=True)
def match_namespace(context, expected_value, match_result, miss_result=''):
    return match_value(context.request.resolver_match.namespace, expected_value, match_result, miss_result)


@register.filter()
def format_duration_verbose(duration):
    result = ''
    duration = int(duration)
    days = duration // (3600 * 24)
    hours = (duration % (3600 * 24)) // 3600
    minutes = (duration % 3600) // 60

    if days > 0:
        result += f'{days} d '

    result += '{} h {} min'.format(hours, minutes)
    return result


@register.filter()
def format_duration(duration):
    result = ''
    duration = int(duration)
    hours = duration // 3600
    minutes = (duration // 60) % 60
    seconds = duration % 60

    if hours > 0:
        result = '{}:'.format(str(hours).zfill(2))

    result += '{}:{}'.format(str(minutes).zfill(2), str(seconds).zfill(2))
    return result


@register.filter()
def seconds_to_minutes(duration):
    duration = int(duration)
    return duration // 60


@register.filter()
def get_color_by_id(obj):
    colors = ['#80b7c2', '#ebb790', '#9cb67c']
    return colors[obj.id % len(colors)]


@register.filter()
def get_initials(obj):
    name_start = obj.name[0] if obj.name else ''
    sname_start = obj.sname[0] if obj.sname else ''
    initials = ''.join([name_start, sname_start])

    if initials and len(initials) >= 1:
        return initials[0]

    return 'A'
