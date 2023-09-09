from wagtail.blocks import (
    CharBlock,
    ListBlock,
    PageChooserBlock,
    RichTextBlock,
    StructBlock,
)
from wagtail.images.blocks import ImageChooserBlock

from base.blocks import BaseStreamBlock


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


class PortfolioStreamBlock(BaseStreamBlock):
    card = CardBlock(group="Sections")
    featured_posts = FeaturedPostsBlock(group="Sections")
