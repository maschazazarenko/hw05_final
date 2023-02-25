from django.views.generic.base import TemplateView


class AboutAuthor(TemplateView):
    """
    Выводит информацию об авторе проекта.
    """
    template_name = 'about/author.html'


class AboutTech(TemplateView):
    """
    Выводит информацию о технологиях,
    с помощью которых написан проект.
    """
    template_name = 'about/tech.html'
