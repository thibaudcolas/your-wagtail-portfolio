from django.db import models
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    PublishingPanel,
)
from wagtail.fields import RichTextField
from wagtail.models import (
    DraftStateMixin,
    PreviewableMixin,
    RevisionMixin,
    TranslatableMixin,
)
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)
from wagtail.snippets.models import register_snippet


@register_setting
class NavigationSettings(ClusterableModel, BaseGenericSetting):
    twitter_url = models.URLField(verbose_name="Twitter URL", blank=True)
    github_url = models.URLField(verbose_name="GitHub URL", blank=True)
    mastodon_url = models.URLField(verbose_name="Mastodon URL", blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("twitter_url"),
                FieldPanel("github_url"),
                FieldPanel("mastodon_url"),
            ],
            "Social settings",
        )
    ]


@register_snippet
class FooterText(
    DraftStateMixin,
    RevisionMixin,
    PreviewableMixin,
    TranslatableMixin,
    models.Model,
):
    """
    This provides editable text for the site footer. Again it is registered
    using `register_snippet` as a function in wagtail_hooks.py to be grouped
    together with the Person model inside the same main menu item. It is made
    accessible on the template via a template tag defined in base/templatetags/
    navigation_tags.py
    """

    body = RichTextField()

    panels = [
        FieldPanel("body"),
        PublishingPanel(),
    ]

    def __str__(self):
        return "Footer text"

    def get_preview_template(self, request, mode_name):
        return "base.html"

    def get_preview_context(self, request, mode_name):
        return {"footer_text": self.body}

    class Meta(TranslatableMixin.Meta):
        verbose_name_plural = "Footer Text"
