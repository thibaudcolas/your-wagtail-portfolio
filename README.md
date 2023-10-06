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
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
)
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)

@register_setting
class NavigationSettings(BaseGenericSetting):
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

### Add a Projects/Skills page

#### New app: portfolio

Commit: [4f10d4e](https://github.com/thibaudcolas/your-wagtail-portfolio/commit/4f10d4e) startapp portfolio

Run `python manage.py startapp portfolio`.

### New page with simple blocks

Commit: [376c6d6](https://github.com/thibaudcolas/your-wagtail-portfolio/commit/376c6d6) Add portfolio page with basic StreamField blocks setup

- Adding blocks first in the `base` app to encourage future reuse.
- Some blocks have custom templates, and for some we rely on the default rendering from Wagtail. We could also override the default in more cases just to fully have control over the HTML, but it’s not needed for basic block types.

Add `"portfolio",` to `INSTALLED_APPS` in `mysite/settings/base.py`.

In `portfolio/models.py`, add the new page type:

```python
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
```

We can then create the reusable blocks. In `portfolio/blocks.py`:

```python
from base.blocks import BaseStreamBlock

class PortfolioStreamBlock(BaseStreamBlock):
    pass
```

For now all blocks will be from a `BaseStreamBlock`, so we can reuse most of our custom blocks across multiple parts of the site in the future.

In `base/blocks.py`:

```python
from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
)
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock


class ImageBlock(StructBlock):
    """
    Custom `StructBlock` for utilizing images with associated caption and
    attribution data
    """

    image = ImageChooserBlock(required=True)
    caption = CharBlock(required=False)
    attribution = CharBlock(required=False)

    class Meta:
        icon = "image"
        template = "base/blocks/image_block.html"


class HeadingBlock(StructBlock):
    """
    Custom `StructBlock` that allows the user to select h2 - h4 sizes for headings
    """

    heading_text = CharBlock(classname="title", required=True)
    size = ChoiceBlock(
        choices=[
            ("", "Select a heading size"),
            ("h2", "H2"),
            ("h3", "H3"),
            ("h4", "H4"),
        ],
        blank=True,
        required=False,
    )

    class Meta:
        icon = "title"
        template = "base/blocks/heading_block.html"


class BaseStreamBlock(StreamBlock):
    """
    Define the custom blocks that `StreamField` will utilize
    """

    heading_block = HeadingBlock()
    paragraph_block = RichTextBlock(icon="pilcrow")
    image_block = ImageBlock()
    embed_block = EmbedBlock(
        help_text="Insert a URL to embed, for example https://www.youtube.com/watch?v=SGJFWirQ3ks",
        icon="media",
    )
```

Some of those blocks have custom templates. For `EmbedBlock`, create `base/templates/base/blocks/embed_block.html`:

```html
{{ self }}
```

For HeadingBlock, create `base/templates/base/blocks/heading_block.html`:

```html
{% if self.size == 'h2' %}
    <h2>{{ self.heading_text }}</h2>
{% elif self.size == 'h3' %}
    <h3>{{ self.heading_text }}</h3>
{% elif self.size == 'h4' %}
    <h4>{{ self.heading_text }}</h4>
{% endif %}
```

For ImageBlock, create `base/templates/base/blocks/image_block.html`:

```html
{% load wagtailimages_tags %}

<figure>
    {% image self.image fill-600x338 loading="lazy" %}
    <figcaption>{{ self.caption }} - {{ self.attribution }}</figcaption>
</figure>
```

Finally create the template for our page type, in `portfolio/templates/portfolio/portfolio_page.html`:

```html
{% extends "base.html" %}

{% load wagtailcore_tags wagtailimages_tags %}

{% block body_class %}template-portfolio{% endblock %}

{% block content %}
    <h1>{{ page.title }}</h1>

    {{ page.body }}
{% endblock %}
```

Make migrations and migrate.

#### More complex blocks

Commit: [b2f5064](https://github.com/thibaudcolas/your-wagtail-portfolio/commit/b2f5064) Add examples of more complex blocks

- Same as above – using [custom block icons](https://docs.wagtail.org/en/stable/topics/streamfield.html#block-icons) to help with telling block types apart
- Also using [`groups`](https://docs.wagtail.org/en/stable/reference/streamfield/blocks.html#block-options) so our custom options are easier to find amongst lists of block types.
- Restrict a PageChooserBlock to only pages of a specific type (here `blog.BlogPage`)

In `portfolio/blocks.py`, we will add two new block types: A "Card" block, and a list of featured blog posts. Import more base block types from Wagtail:

```python
from wagtail.blocks import (
    CharBlock,
    ListBlock,
    PageChooserBlock,
    RichTextBlock,
    StructBlock,
)
from wagtail.images.blocks import ImageChooserBlock
```

Creare our two new block types:

```python
class CardBlock(StructBlock):
    heading = CharBlock()
    # To improve consistency in how blocks appear, we only allow certain rich text features to be used.
    # For example, headings aren’t available because the section will already have a heading.
    text = RichTextBlock(features=["bold", "italic", "link"])
    image = ImageChooserBlock(required=False)

    class Meta:
        icon = "form"
        template = "portfolio/blocks/card_block.html"


class FeaturedPostsBlock(StructBlock):
    heading = CharBlock()
    text = RichTextBlock(features=["bold", "italic", "link"], required=False)
    posts = ListBlock(PageChooserBlock(page_type="blog.BlogPage"))

    class Meta:
        icon = "folder-open-inverse"
        template = "portfolio/blocks/featured_posts_block.html"
```

Update our `PortfolioStreamBlock` to reuse those new block types.

```python
class PortfolioStreamBlock(BaseStreamBlock):
    card = CardBlock(group="Portfolio sections")
    featured_posts = FeaturedPostsBlock(group="Portfolio sections")
```

Make migrations and migrate.

Create the templates for those new block types: first `portfolio/templates/portfolio/blocks/card_block.html`,

```html
{% load wagtailcore_tags wagtailimages_tags %}
<div class="card">
    <h3>{{ self.heading }}</h3>
    <div>{{ self.text|richtext }}</div>
    {% if self.image %}
        {% image self.image width-480 %}
    {% endif %}
</div>
```

Then `portfolio/templates/portfolio/blocks/featured_posts_block.html`:

```html
{% load wagtailcore_tags %}
<div>
    <h2>{{ self.heading }}</h2>
    {% if self.text %}
        <p>{{ self.text|richtext }}</p>
    {% endif %}

    <div class="grid">
        {% for page in self.posts %}
            <div class="card">
                <p><a href="{% pageurl page %}">{{ page.title }}</a></p>
                <p>{{ page.specific.date }}</p>
            </div>
        {% endfor %}
    </div>
</div>
```

Update your project stylesheet so those block types look nicer:

```css
.card {
  max-width: min-content;
  min-width: 50vw;
  border: 2px solid;
  padding: 0 10px;
  margin-bottom: 10px;
}

.card img {
  display: block;
  margin: 0 -10px;
  max-width: 90vw;
  border-top: 2px solid;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px;
}

.grid .card {
  min-width: 140px;
  max-width: unset;
}
```

Make migrations and migrate if you haven’t already. Then add content in the CMS.

### Search

#### Custom search view

Commit: [9d1cac6](https://github.com/thibaudcolas/your-wagtail-portfolio/commit/9d1cac6) Add minimal search setup

- `query.add_hit` is only there to keep track of query popularity _if_ we wanted to introduce promoted search results later (see user guide).
- Nothing special to Wagtail in the search view. Pagination and all are built-in Django features.

The `search` app is already present on the site, as it’s part of Wagtail’s starter project template which we used. We can look at the `search` view in `search/views.py` but there is nothing to customize for a simple site search:

```python
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse

from wagtail.models import Page
from wagtail.search.models import Query


def search(request):
    search_query = request.GET.get("query", None)
    page = request.GET.get("page", 1)

    # Search
    if search_query:
        search_results = Page.objects.live().search(search_query)
        query = Query.get(search_query)

        # Record hit
        query.add_hit()
    else:
        search_results = Page.objects.none()

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return TemplateResponse(
        request,
        "search/search.html",
        {
            "search_query": search_query,
            "search_results": search_results,
        },
    )
```

We can make a few nice-to-have customizations to the template which displays the results. First, add `| <a href="/search/">Search</a>` to our `header.html` as the last menu item, so all our pages link to the search form.

Then, in `search/templates/search/search.html`, we will:

- Convert the `<ul>` list to `<ol>` for better semantics – search results are ordered by relevance.
- Add a message at the top of the results to summarize the query and number of results.
- Add page counts to the pagination at the bottom.

Summary before the `<ol></ol>` results list:

```html
<p>You searched{% if search_query %} for “{{ search_query }}”{% endif %}, {{ search_results.paginator.count }} result{{ search_results.paginator.count|pluralize }} found.</p>
```

Page counts after the `<ol></ol>` results list:

```html
{% if search_results.paginator.num_pages > 1 %}
    <p>Page {{ search_results.number }} of {{ search_results.paginator.num_pages }}, showing {{ search_results|length }} result{{ search_results|pluralize }} out of {{ search_results.paginator.count }}</p>
{% endif %}
```

#### Make more page content searchable

TODO. Sample code:

```python
from wagtail.search import index

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]
```

### Deployment

#### Set up an image storage bucket with Backblaze B2

We are going to use Backblaze B2 as an image storage and delivery service. Storing our images separately from the site gives a lot of performance, security, and reliability benefits. Backblaze B2 offers a very generous free tier of 10GB of storage and plenty of bandwidth.

The B2 service works exactly like Amazon Web Services’ S3, hence why "AWS" and "S3" show up a lot in our configuration below. We will access our data in B2 just like if we were using S3.

[Sign up for B2 Cloud Storage](https://www.backblaze.com/sign-up/cloud-storage) from [Backblaze](https://www.backblaze.com/):

1. [Sign up](https://www.backblaze.com/sign-up/cloud-storage). Set your account region to a specific one if you want to.
2. Sign in
3. Go to Account > My Settings, and under **Security:** click **Verify Email**
4. Send the code, go to your mailbox, click the verification link

Create a new bucket:

1. Go to B2 Cloud Storage > Buckets, and click **Create a Bucket**
2. Bucket Unique Name: use something unique, for example `yourname-wagtail-portfolio` (replacing `yourname` with your own name)
3. Files in Bucket are: Select `Public`
4. Default Encryption: Select `Disable`
5. Object Lock: Select `Disable`
6. Click **Create a Bucket**

Note the bucket’s name, endpoint, and place them in a new `.env.production` file, in the following format:

```txt
AWS_STORAGE_BUCKET_NAME=
AWS_S3_ENDPOINT_URL=https://
AWS_S3_REGION_NAME=
AWS_S3_ACCESS_KEY_ID=
AWS_S3_SECRET_ACCESS_KEY=
DJANGO_ALLOWED_HOSTS=
DJANGO_CSRF_TRUSTED_ORIGINS=https://
DJANGO_SETTINGS_MODULE=mysite.settings.production
```

- Use `AWS_STORAGE_BUCKET_NAME` for the bucket Name
- Use `AWS_S3_ENDPOINT_URL` for the bucket Endpoint
- For `AWS_S3_REGION_NAME`, Determine the region from the endpoint. For example, for `s3.us-east-005.backblazeb2.com`, the region is `us-east-005`.

Here is an example with pretend values:

```txt
AWS_STORAGE_BUCKET_NAME=yourname-wagtail-portfolio
AWS_S3_ENDPOINT_URL=https://s3.us-east-005.backblazeb2.com
AWS_S3_REGION_NAME=us-east-005
AWS_S3_ACCESS_KEY_ID=
AWS_S3_SECRET_ACCESS_KEY=
DJANGO_ALLOWED_HOSTS=
DJANGO_CSRF_TRUSTED_ORIGINS=https://
DJANGO_SETTINGS_MODULE=mysite.settings.production
```

Now we will get the secret keys that must never be shared:

1. Go to Account > Application Keys, and click **Add a New Application Key**
2. Name of Key: a unique name for you to remember. For example, "yourname-wagtail-portfolio-key"
3. Allow access to Bucket(s): choose the bucket you created
4. Type of Access: Read and Write
5. Allow List All Bucket Names: leave this unticked
6. File name prefix: leave empty
7. Duration: leave empty
8. Click "Create New Key"
9. In your `.env.production`, add the `keyID` after `AWS_S3_ACCESS_KEY_ID=`.
10. In your `.env.production`, add the `applicationKey` after `AWS_S3_SECRET_ACCESS_KEY=`.

Make sure to never commit or share your `.env.production` file. Anyone with those keys could steal or delete all of your files.

If you lost your secret application key, create a new key following the above process.

#### Set up Fly.io hosting

Sign up to [Fly.io](https://fly.io/), and make sure to verify your account’s email address and add a credit card to fully activate your account.

1. Go to Sign up page
2. Verify your email. If this fails, do it again from the dashboard.
3. Add your credit card details. You won’t be charged, this is so you are allowed to create a project in Fly.

Install [flyctl](https://fly.io/docs/hands-on/install-flyctl/)

Sign in with:

```bash
fly auth login
```

Output:

```bash
Opening https://fly.io/app/auth/cli/ ...

Waiting for session... Done
successfully logged in as <your email>
```

> For Damilola: From now on we follow the [Existing Django Apps](https://fly.io/docs/django/getting-started/existing/) guide almost to the letter.

Create your project with:

```bash
fly launch
```

1. Select your app name
1. Select the same region as your Backblaze bucket
1. Postgres database: yes
1. Configuration: smallest possible

Output:

```bash
Creating app in /Users/thibaudcolas/Dev/wagtail/your-wagtail-portfolio
Scanning source code
Detected a Django app
? Choose an app name (leave blank to generate one): yourname-wagtail-portfolio
automatically selected personal organization: yourname
Some regions require a paid plan (bom, fra, maa).
See https://fly.io/plans to set up a plan.

? Choose a region for deployment: Stockholm, Sweden (arn)
App will use 'arn' region as primary

Created app 'yourname-wagtail-portfolio' in organization 'personal'
Admin URL: https://fly.io/apps/yourname-wagtail-portfolio
Hostname: yourname-wagtail-portfolio.fly.dev
? Overwrite "/Users/thibaudcolas/Dev/wagtail/your-wagtail-portfolio/Dockerfile"? Yes
Set secrets on yourname-wagtail-portfolio: SECRET_KEY
? Would you like to set up a Postgresql database now? Yes
? Select configuration: Development - Single node, 1x shared CPU, 256MB RAM, 1GB disk
? Scale single node pg to zero after one hour? Yes
Creating postgres cluster in organization personal
Creating app...
Setting secrets on app yourname-wagtail-portfolio-db...
Provisioning 1 of 1 machines with image flyio/postgres-flex:15.3
Waiting for machine to start...
Machine 328744e1c53428 is created
==> Monitoring health checks
  Waiting for 328744e1c53428 to become healthy (started, 3/3)

Postgres cluster yourname-wagtail-portfolio-db created
  Username:    postgres
  Password:    <password>
  Hostname:    yourname-wagtail-portfolio-db.internal
  Flycast:     fdaa:3:3975:0:1::2
  Proxy port:  5432
  Postgres port:  5433
  Connection string: postgres://postgres:<password>@yourname-wagtail-portfolio-db.flycast:5432

Save your credentials in a secure place -- you won't be able to see them again!

Connect to postgres
Any app within the yourname organization can connect to this Postgres using the above connection string

Now that you've set up Postgres, here's what you need to understand: https://fly.io/docs/postgres/getting-started/what-you-should-know/
Checking for existing attachments
Registering attachment
Creating database
Creating user

Postgres cluster yourname-wagtail-portfolio-db is now attached to yourname-wagtail-portfolio
The following secret was added to yourname-wagtail-portfolio:
  DATABASE_URL=postgres://yourname_wagtail_portfolio:<password>@yourname-wagtail-portfolio-db.flycast:5432/yourname_wagtail_portfolio?sslmode=disable
Postgres cluster yourname-wagtail-portfolio-db is now attached to yourname-wagtail-portfolio
? Would you like to set up an Upstash Redis database now? No
Wrote config file fly.toml

[INFO] Python 3.11.5 was detected. 'python:3.11-slim-bullseye' image will be set in the Dockerfile.

Validating /Users/thibaudcolas/Dev/wagtail/your-wagtail-portfolio/fly.toml
Platform: machines
✓ Configuration is valid

Multiple 'settings.py' files were found in your Django application:
[venv/lib/python3.11/site-packages/rest_framework/settings.py, venv/lib/python3.11/site-packages/treebeard/tests/settings.py, venv/lib/python3.11/site-packages/wagtail/test/settings.py, venv/lib/python3.11/site-packages/wagtail/tests/settings.py]
It's not recommended to have multiple 'settings.py' files.
Instead, you can have a 'settings/' folder with the settings files according to the different environments (e.g., local.py, staging.py, production.py).
In this case, you can specify which settings file to use when running the Django application by setting the 'DJANGO_SETTINGS_MODULE' environment variable to the corresponding settings file.

'STATIC_ROOT' setting was detected in 'venv/lib/python3.11/site-packages/wagtail/test/settings.py'!
Static files will be collected during build time by running 'python manage.py collectstatic' on Dockerfile.

A default SECRET_KEY was not detected in 'venv/lib/python3.11/site-packages/wagtail/test/settings.py'!
A generated SECRET_KEY "<password>" was set on Dockerfile for building purposes.
Optionally, you can use django.core.management.utils.get_random_secret_key() to set the SECRET_KEY default value in your venv/lib/python3.11/site-packages/wagtail/test/settings.py.
```

At this point, we have generated the files as per this commit:

Commit: [cc85865](https://github.com/thibaudcolas/your-wagtail-portfolio/commit/cc85865) Add fly.io generated production setup

#### Configuration files

Commit: [7246547](https://github.com/thibaudcolas/your-wagtail-portfolio/commit/7246547) Add production setup customizations

We shouldn’t have to change the project’s code, but will have to change configuration files.

First, in `.gitignore`, add at the end:

```txt
.env*
```

Inn `.dockerignore`, add at the end:

```txt
.env*
media
```

And on the last line of `Dockerfile`, switch to 1 worker so our site works better with Fly.io’s low memory allowance:

```Dockerfile
CMD ["gunicorn", "--bind", ":8000", "--workers", "1", "mysite.wsgi"]
```

And in `fly.toml`:

1. Remove the `console_command = "/code/manage.py shell"`
2. Right where `console_command` was, add a `[deploy]` section:

```toml

[deploy]
    release_command = "/code/manage.py migrate --noinput"

```

In `requirements.txt`, add our production dependencies:

```txt
# Production dependencies.
## gunicorn: runs the server in Docker.
gunicorn>=21.2.0,<22.0.0
## psycopg: connects to the Postgres database.
psycopg[binary]>=3.1.10,<3.2.0
## dj-database-url: connects to the Postgres database.
dj-database-url>=2.1.0,<3.0.0
## whitenoise: servers static files.
whitenoise>=5.0,<5.1
## django-storages: connects to Backblaze B2.
django-storages[s3]>=1.14.0,<2.0.0
```

In `mysite/settings/production.py`,

```python
import os
import random
import string
import dj_database_url

from .base import *

DEBUG = False

DATABASES = {
    "default": dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True
    )
}

# SECRET_KEY *should* be specified in the environment.
SECRET_KEY = os.environ["SECRET_KEY"]

# Make sure Django can detect a secure connection properly on Heroku:
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Force HTTPS redirect (enabled by default!)
# https://docs.djangoproject.com/en/stable/ref/settings/#secure-ssl-redirect
SECURE_SSL_REDIRECT = True

# IMPORTANT: Set this to a real hostname when using this in production!
# See https://docs.djangoproject.com/en/3.2/ref/settings/#allowed-hosts
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

CSRF_TRUSTED_ORIGINS = os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")

# Use the console email backend as we don’t configure emails in this tutorial.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

if "AWS_STORAGE_BUCKET_NAME" in os.environ:
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
    AWS_S3_ACCESS_KEY_ID = os.getenv("AWS_S3_ACCESS_KEY_ID")
    AWS_S3_SECRET_ACCESS_KEY = os.getenv("AWS_S3_SECRET_ACCESS_KEY")

    INSTALLED_APPS.append("storages")

    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
        },
    },
}

# Allow the redirect importer to work in load-balanced / cloud environments.
# https://docs.wagtail.org/en/stable/reference/settings.html#redirects
WAGTAIL_REDIRECTS_FILE_STORAGE = "cache"

try:
    from .local import *
except ImportError:
    pass
```

In our `.env.production`, add extra settings:

1. `DJANGO_ALLOWED_HOSTS` must match your fly.io project name, for example `yourname-wagtail-portfolio.fly.dev`
2. `DJANGO_CSRF_TRUSTED_ORIGINS` must match your project’s domain name, for example `https://yourname-wagtail-portfolio.fly.dev`
3. `DJANGO_SETTINGS_MODULE` must be `mysite.settings.production`

Here is an example:

```text
AWS_STORAGE_BUCKET_NAME=yourname-wagtail-portfolio
AWS_S3_ENDPOINT_URL=https://s3.us-east-005.backblazeb2.com
AWS_S3_REGION_NAME=us-east-005
AWS_S3_ACCESS_KEY_ID=youracceskeyid
AWS_S3_SECRET_ACCESS_KEY=yourapplicationsecretkey
DJANGO_ALLOWED_HOSTS=yourname-wagtail-portfolio.fly.dev
DJANGO_CSRF_TRUSTED_ORIGINS=https://yourname-wagtail-portfolio.fly.dev
DJANGO_SETTINGS_MODULE=mysite.settings.production
```

Set those secrets for Fly to use:

```bash
flyctl secrets import < .env.production
```

Finally,

```bash
fly deploy --ha=false
```

Output:

```txt
==> Verifying app config
Validating /Users/thibaudcolas/Dev/wagtail/your-wagtail-portfolio/fly.toml
Platform: machines
✓ Configuration is valid
--> Verified app config
==> Building image
Remote builder fly-builder-frosty-river-8630 ready
==> Building image with Docker
--> docker host: 20.10.12 linux x86_64
[+] Building 3.5s (12/12) FINISHED
 => [internal] load build definition from Dockerfile                                                                              0.1s
 => => transferring dockerfile: 32B                                                                                               0.1s
 => [internal] load .dockerignore                                                                                                 0.1s
 => => transferring context: 34B                                                                                                  0.1s
 => [internal] load metadata for docker.io/library/python:3.11-slim-bullseye                                                      0.7s
 => [internal] load build context                                                                                                 2.7s
 => => transferring context: 2.00MB                                                                                               2.6s
 => [1/7] FROM docker.io/library/python:3.11-slim-bullseye@sha256:                                                                0.0s
 => CACHED [2/7] RUN mkdir -p /code                                                                                               0.0s
 => CACHED [3/7] WORKDIR /code                                                                                                    0.0s
 => CACHED [4/7] COPY requirements.txt /tmp/requirements.txt                                                                      0.0s
 => CACHED [5/7] RUN set -ex &&     pip install --upgrade pip &&     pip install -r /tmp/requirements.txt &&     rm -rf /root/.c  0.0s
 => CACHED [6/7] COPY . /code                                                                                                     0.0s
 => CACHED [7/7] RUN python manage.py collectstatic --noinput                                                                     0.0s
 => exporting to image                                                                                                            0.0s
 => => exporting layers                                                                                                           0.0s
 => => writing image sha256:0d67cc955f56094d5a2a8686a1c3eda26e0370f92f0831fcee05c1068639d80c                                      0.0s
 => => naming to registry.fly.io/yourname-wagtail-portfolio:deployment-01HC2X8ST21VVZ0D9TQZZN47X3                                 0.0s
--> Building image done
==> Pushing image to fly
The push refers to repository [registry.fly.io/yourname-wagtail-portfolio]
db09b5fac7d9: Layer already exists
b52ae83836ea: Layer already exists
ee8c593bb5aa: Layer already exists
4fcc9dfc4b2d: Layer already exists
5f70bf18a086: Layer already exists
e0d2d6536ad2: Layer already exists
3ad0973549a4: Layer already exists
9224fa8e5ddb: Layer already exists
2cc7bd46e795: Layer already exists
aa065d85cfdc: Layer already exists
10764c37bcbc: Layer already exists
deployment-01HC2X8ST21VVZ0D9TQZZN47X3: digest: sha256:55876e955c549adabf65ee66daec8cdba257ee93f0d8747a559ea3d5850fa830 size: 2625
--> Pushing image done
image: registry.fly.io/yourname-wagtail-portfolio:deployment-01HC2X8ST21VVZ0D9TQZZN47X3
image size: 474 MB

Watch your deployment at https://fly.io/apps/yourname-wagtail-portfolio/monitoring

Running yourname-wagtail-portfolio release_command: /code/manage.py migrate

-------
 ✔ release_command 4d89dee2c7e187 completed successfully
-------
This deployment will:
 * create 1 "app" machine

No machines in group app, launching a new machine

WARNING The app is not listening on the expected address and will not be reachable by fly-proxy.
You can fix this by configuring your app to listen on the following addresses:
  - 0.0.0.0:8000
Found these processes inside the machine with open listening sockets:
  PROCESS        | ADDRESSES
-----------------*--------------------------------------
  /.fly/hallpass | [fdaa:3:3975:a7b:e8:143e:4c7c:2]:22

Finished launching new machines
-------
NOTE: The machines for [app] have services with 'auto_stop_machines = true' that will be stopped when idling


Visit your newly deployed app at https://yourname-wagtail-portfolio.fly.dev/
```

Congratulations! Your site is now live, but needs content added.

```bash
flyctl ssh console
```

And run:

```bash
DJANGO_SUPERUSER_USERNAME=admin DJANGO_SUPERUSER_EMAIL=admin@example.com DJANGO_SUPERUSER_PASSWORD=changeme /code/manage.py createsuperuser --noinput
```

And then `exit`.

Go to https://yourname-wagtail-portfolio.fly.dev/admin/ and add content!

---

Error with an unverified account:

```txt
Error: error creating a new machine: failed to launch VM: To create more than 1 machine per app please add a payment method. https://fly.io/dashboard/<account>/billing
Please note that release commands run in their own ephemeral machine, and therefore count towards the machine limit. (Request ID: 01HC2X4FAQ7PT7JEKFKZK5AJM9-lhr)
```

### Optional steps

#### Convert BlogPage to use StreamField

#### Organise the Wagtail admin with a SnippetViewSetGroup

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
