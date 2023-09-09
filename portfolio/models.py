from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel

from portfolio.blocks import PortfolioStreamBlock


class PortfolioPage(Page):
    """
    A page to list our projects and skills.
    """
    parent_page_types = ["home.HomePage"]

    body = StreamField(
        PortfolioStreamBlock(),
        blank=True,
        use_json_field=True,
        help_text="Use this section to list your projects and skills.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]
