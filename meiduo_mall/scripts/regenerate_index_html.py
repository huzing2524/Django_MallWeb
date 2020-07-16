#!/user/bin/env python
import sys
import os
import django

sys.path.insert(0, "../")

if not os.getenv("DJANGO_SETTINGS_MODULE"):
    os.environ["DJANGO_SETTINGS_MODULE"] = "meiduo_mall.settings.dev"

# django初始化，加载django功能
django.setup()

from contents.crons import generate_static_index_html

if __name__ == '__main__':
    generate_static_index_html()
