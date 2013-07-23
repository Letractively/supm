# Scrapy settings for supm project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'supm'

SPIDER_MODULES = ['supm.spiders']
NEWSPIDER_MODULE = 'supm.spiders'
ITEM_PIPELINES = ['supm.pipelines.publicationsPipeline']
DOWNLOAD_DELAY = 0.5
COOKIES_ENABLED = False
#CONCURRENT_REQUESTS = 1 #default 16
#CONCURRENT_ITEMS = 1
DOWNLOADER_DEBUG = False

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'supm (+http://www.yourdomain.com)'
