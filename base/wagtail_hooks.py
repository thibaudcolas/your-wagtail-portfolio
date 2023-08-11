from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from base.models import FooterText
from blog.models import Author


class FooterTextViewSet(SnippetViewSet):
    model = FooterText
    icon = "pilcrow"
    search_fields = ("body",)


class AuthorViewSet(SnippetViewSet):
    model = Author
    icon = "user"


class SiteDataSnippetViewSetGroup(SnippetViewSetGroup):
    menu_label = "Site Data"
    menu_icon = "info-circle"  # change as required
    menu_order = 300  # will put in 4th place (000 being 1st, 100 2nd)
    items = (FooterTextViewSet, AuthorViewSet)

register_snippet(SiteDataSnippetViewSetGroup)
