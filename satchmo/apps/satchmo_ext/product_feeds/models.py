from satchmo_utils.signals import collect_urls
from satchmo_store import shop
from urls import add_feed_urls

collect_urls.connect(add_feed_urls, sender=shop)
