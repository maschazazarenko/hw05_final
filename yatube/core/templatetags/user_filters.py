from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """
    Функция добавит пользовательские фильтры.
    """
    return field.as_widget(attrs={'class': css})
