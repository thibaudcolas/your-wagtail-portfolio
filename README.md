# Your first Wagtail site

Starts from Wagtail’s getting started tutorial ([1a72d82](https://github.com/thibaudcolas/your-wagtail-portfolio/commit/1a72d82)), ends with a live site! (TODO)

## New tutorial sections

### Customize the home page

Commit: [5081fda](https://github.com/thibaudcolas/your-wagtail-portfolio/commit/5081fda) Add new homepage fields

#### Add a field for a headshot or graphic, a field for text that can include a short bio or enticing “hire me” text.

To highlight:

- `hero_cta_link`, a `ForeignKey` to a Page instance
    - Explain `on_delete` and `related_name` if not explained before
- `MultiFieldPanel` to group related fields
- `firstof` template tag usage to display `hero_cta` if set, otherwise linked page’s title

In `home/models.py`, add:

```python
from wagtail.admin.panels import FieldPanel, MultiFieldPanel


class HomePage(Page):
    # Hero section of HomePage
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Homepage image",
    )
    hero_text = models.CharField(
        blank=True,
        max_length=255, help_text="Write an introduction for the site"
    )
    hero_cta = models.CharField(
        blank=True,
        verbose_name="Hero CTA",
        max_length=255,
        help_text="Text to display on Call to Action",
    )
    hero_cta_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Hero CTA link",
        help_text="Choose a page to link to for the Call to Action",
    )

    # Body section of the HomePage
    body = RichTextField(blank=True)
```

In HomePage content_panels:

```python
        MultiFieldPanel(
            [
                FieldPanel("image"),
                FieldPanel("hero_text"),
                FieldPanel("hero_cta"),
                FieldPanel("hero_cta_link"),
            ],
            heading="Hero section",
        ),
```

#### Add a documents field for a downloadable copy of a resume/CV to demonstrate how document fields work 

TODO / later step in the tutorial

#### Add template for displaying these items

Make migrations and migrate.

Update `home_page.html`:

```html
{% load wagtailcore_tags wagtailimages_tags %}

{% block content %}
    <div>
        <h1>{{ page.title }}</h1>
        {% image page.image fill-480x320 %}
        <p>{{ page.hero_text }}</p>
        {% if page.hero_cta_link %}
            <a href="{% pageurl page.hero_cta_link %}">
                {% firstof page.hero_cta page.hero_cta_link.title %}
            </a>
        {% endif %}
    </div>
```

### Create footer for all pages

#### New app: base

Commit: [a4b7329](https://github.com/thibaudcolas/your-wagtail-portfolio/commit/a4b7329) Add base app boilerplate from Django startapp command

Run `python manage.py startapp base`.

#### Create a Settings model for footer icons

Commit: [6c8979b](https://github.com/thibaudcolas/your-wagtail-portfolio/commit/6c8979b) Add footer template partial with NavigationSettings model for social media links

- First use of Wagtail’s site settings feature.
- Customize the fields based on your preferred socials.

In `base/models.py`:

```python
from django.db import models
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
)
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)

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
```

In `mysite/settings/base.py` updated `INSTALLED_APPS` to add:

```python
    "base",
    "wagtail.contrib.settings",
```

And also update `context_processors` in `TEMPLATES` to add:

```python
"wagtail.contrib.settings.context_processors.settings",
```

Make migrations and migrate

#### Create template for the site footer

- First use of `include` / Django template partials. Important concept.
- Using `with` template tag for performance and brevity: only load data from the NavigationSettings model once.

In `mysite/templates/includes/footer.html`:

```html
<footer>
    <p>Built with Wagtail</p>

    {% with twitter_url=settings.base.NavigationSettings.twitter_url github_url=settings.base.NavigationSettings.github_url mastodon_url=settings.base.NavigationSettings.mastodon_url %}
        {% if twitter_url or github_url or mastodon_url %}
            <p>
                Follow me on:
                {% if github_url %}
                    <a href="{{ github_url }}">GitHub</a>
                {% endif %}
                {% if twitter_url %}
                    <a href="{{ twitter_url }}">Twitter</a>
                {% endif %}
                {% if mastodon_url %}
                    <a href="{{ mastodon_url }}">Mastodon</a>
                {% endif %}
            </p>
        {% endif %}
    {% endwith %}
</footer>
```

#### Update base.html to include template

In `base.html`, add:

```html
{% include "includes/footer.html" %}
```

### Show footer text with a snippet

#### Create FooterText snippet model

Commit: [b8f417e](https://github.com/thibaudcolas/your-wagtail-portfolio/commit/b8f417e) Add footer_text with snippet, custom template tag

- Supports drafts, previews, revisions, translations.
- Previews in particular are fully set up.

In `base/models.py`:

```python
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
```

Make migrations and migrate

#### New template tag

First time we create a custom template tag (`inclusion_tag` which combines a template with Django data). Making sure to only display footer text that is published (`.filter(live=True)`), like blog posts index page.

Create:

- `base/templatetags/` folder
- `base/templatetags/__init__.py` file (empty)
- `base/templatetags/navigation_tags.py` file

In this last file:

```python
from django import template

from base.models import FooterText

register = template.Library()


@register.inclusion_tag("base/includes/footer_text.html", takes_context=True)
def get_footer_text(context):
    # Get the footer text from the context if exists,
    # so that it's possible to pass a custom instance e.g. for previews
    # or page types that need a custom footer
    footer_text = context.get("footer_text", "")

    # If the context doesn't have footer_text defined, get one that's live
    if not footer_text:
        instance = FooterText.objects.filter(live=True).first()
        footer_text = instance.body if instance else ""

    return {
        "footer_text": footer_text,
    }
```

Create the tag’s template in `base/templates/base/includes/footer_text.html`:

```html
{% load wagtailcore_tags %}

<div>
    {{ footer_text|richtext }}
</div>
```

#### Use new get_footer_text in footer template

In `mysite/templates/includes/footer.html`:

```html
{% load navigation_tags %}

{% get_footer_text %}
```

### Set up a menu for linking to the homepage and other pages as you add them

Commit: [7f8b9be](https://github.com/thibaudcolas/your-wagtail-portfolio/commit/7f8b9be) Add a simple site menu implementation

#### Create a new template tag leveraging Wagtail’s "Show in menus" feature

- Leverages Wagtail’s `Site` model to retrieve the root page of the site

In `base/templatetags/navigation_tags.py`:

```python
from wagtail.models import Site


@register.simple_tag(takes_context=True)
def get_site_root(context):
    # This returns a core.Page. The main menu needs to have the site.root_page
    # defined else will return an object attribute error ('str' object has no
    # attribute 'get_children')
    return Site.find_for_request(context["request"]).root_page
```

#### Create header template

- QuerySet: `site_root.get_children.live.in_menu` corresponds to `site_root.get_children().live().in_menu()`
- Fetches all child pages of the HomePage which are live and have the "Show in menus" checkbox ticked

In `mysite/templates/includes/header.html`:

```html
{% load wagtailcore_tags navigation_tags %}
<header>
    {% get_site_root as site_root %}
    <nav>
        <p>
        <a href="{% pageurl site_root %}">Home</a> |
        {% for menuitem in site_root.get_children.live.in_menu %}
            <a href="{% pageurl menuitem %}">{{ menuitem.title }}</a>
        {% endfor %}
        </p>
    </nav>
</header>
```

#### Add menu to base.html

In `base.html`, add:

```html
{% include "includes/header.html" %}
```

---

Make sure to click "Show in menus" in some of your top-level pages for them to appear in the menu.

### Styling of the site

Commit: [be97d57](https://github.com/thibaudcolas/your-wagtail-portfolio/commit/be97d57) Add basic site theme, with favicon, page layout, styled header and footer

- Moving `wagtailuserbar` for a better experience for keyboard and screen reader users.
- Adding a `main` element to the page for better semantics.
- In CSS, using a box-sizing reset, system font stack, and styling the body so the footer is always at the bottom of the page.
- Adding styles for the homepage only with the `template-homepage` class defined in the `body_class` block.

#### Templates refactoring

In `mysite/templates/base.html`, change:

- Remove the `wagtailuserbar` template tag and its reference in `load`
- Wrap `{% block content %}{% endblock %}` with a `<main>` tag: `<main>{% block content %}{% endblock %}</main>`
- Add a favicon in `<head>`, with inline SVG:

```html
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🍩</text></svg>"/>
```

In `mysite/templates/includes/header.html`, change:

- The "Home" link text to `{{ site_root.title }}`, so we use the homepage’s title as the link text.
- Right before the menu items’ `{% endfor %}`, add: `{% if not forloop.last %} | {% endif %}`, so we show a separator between menu items.
- Add `{% wagtailuserbar "top-right" %}` as the last item in the header, before the `</header>` closing tag (and add `wagtailuserbar` to the `load` tag at the top of the file).


#### Add CSS

In `mysite/static/css/mysite.css`, add:

```css
*,
::before,
::after {
  box-sizing: border-box;
}

html {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, Roboto, "Helvetica Neue", Arial, sans-serif, Apple Color Emoji, "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
}

body {
  min-height: 100vh;
  max-width: 800px;
  margin: 0 auto;
  padding: 10px;
  display: grid;
  gap: 3vw;
  grid-template-rows: min-content 1fr min-content;
}

a {
  color: currentColor;
}

footer {
  border-top: 2px dotted;
  text-align: center;
}

header {
  border-bottom: 2px dotted;
}

.template-homepage main {
  text-align: center;
}
```

#### Skip link

Commit: [52446af](https://github.com/thibaudcolas/your-wagtail-portfolio/commit/52446af) Add a skip-link for keyboard users

We

- In `mysite/templates/base.html`, add an id to the main element: `<main id="main">`.
- Then in `mysite/templates/includes/header.html`, after the `<header>` opening tag, add: `<a href="#main" class="skip-link">Skip to content</a>`.

Finally in our stylesheet, add skip link styles:

```css
.skip-link {
  position: absolute;
  top: -30px;
}

.skip-link:focus-visible {
  top: 5px;
}
```

### Create a contact page

Commit: [93afc91](https://github.com/thibaudcolas/your-wagtail-portfolio/commit/93afc91) Add contact page

#### Demonstrate how to create a Wagtail form page

In `base/models.py`, add:

```python
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldRowPanel,
    InlinePanel,
)
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.panels import FormSubmissionsPanel

class FormField(AbstractFormField):
    page = ParentalKey('FormPage', on_delete=models.CASCADE, related_name='form_fields')


class FormPage(AbstractEmailForm):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel('intro'),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('thank_you_text'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address'),
                FieldPanel('to_address'),
            ]),
            FieldPanel('subject'),
        ], "Email"),
    ]
```

Make migrations and migrate.

Then create:

- `base/templates/base/form_page.html`
- `base/templates/base/form_page_landing.html`

In `form_page.html`:

```html
{% extends "base.html" %}
{% load wagtailcore_tags %}

{% block body_class %}template-formpage{% endblock %}

{% block content %}
    <h1>{{ page.title }}</h1>
    <div>{{ page.intro|richtext }}</div>

    <form class="page-form" action="{% pageurl page %}" method="POST">
        {% csrf_token %}
        {{ form.as_div }}
        <button type="Submit">Submit</button>
    </form>
{% endblock content %}
```

In `form_page_landing.html`:

```html
{% extends "base.html" %}
{% load wagtailcore_tags %}

{% block body_class %}template-formpage{% endblock %}

{% block content %}
    <h1>{{ page.title }}</h1>
    <div>{{ page.thank_you_text|richtext }}</div>
{% endblock content %}
```

And finally in `mysite.css`, add basic form styles:

```css
.page-form label {
  display: block;
  margin-top: 10px;
  margin-bottom: 5px;
}

.page-form :is(textarea, input, select) {
  width: 100%;
  max-width: 500px;
  min-height: 40px;
  margin-top: 5px;
  margin-bottom: 10px;
}

.page-form .helptext {
  font-style: italic;
}
```

#### Template for our form page

### Convert BlogPage to use StreamField

### Add a Projects/Skills page

### Add search functionality to the website to demonstrate Wagtail search basics

### Deployment


### Organise the Wagtail admin with a SnippetViewSetGroup

Commit: [56c32fa](https://github.com/thibaudcolas/your-wagtail-portfolio/commit/56c32fa) Register models with a SnippetViewSetGroup

- Not necessarily the most important thing, just demonstrates more Wagtail features. Perhaps later in the tutorial with other Wagtail customizations?
- Showcases `wagtail_hooks.py`

Remove `@register_snippet` on FooterText model, then proceed.

New file: `base/wagtail_hooks.py`

```python

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
```



## Potential tutorial additions

Solid options:

```
Django Debug Toolbar
Sitemap
parent_page_types and subpage_types
```

Possible options, not as compelling:

```
Custom management commands
Choice fields
Views
Messages
REST API
Wagtail hooks
register_icons
construct_wagtail_userbar and AccessibilityItem
Search promotion
Embeds
```
