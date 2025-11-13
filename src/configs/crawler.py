from crawl4ai import CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

prune_filter = PruningContentFilter(
    threshold=0.2,
    threshold_type="dynamic",
    min_word_threshold=0,
)

crawler_config = CrawlerRunConfig(
    exclude_all_images=True,
    keep_data_attributes=False,
    exclude_external_links=True,
    exclude_internal_links=True,
    exclude_social_media_links=True,
    excluded_tags=[
        "script",
        "style",
        "nav",
        "navbar",
        "footer",
        "aside",
        "form",
        "header",
        "button",
        "input",
        "select",
        "textarea",
        "svg",
        "iframe",
    ],
    markdown_generator=DefaultMarkdownGenerator(
        content_filter=prune_filter,
        options={"citations": False},
    ),
)
