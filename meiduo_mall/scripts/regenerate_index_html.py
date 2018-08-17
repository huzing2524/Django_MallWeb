#!/user/bin/env python
import sys
import os
import django

from contents.crons import generate_static_index_html

sys.path.insert(0, "../")

if not os.getenv("DJANGO_SETTINGS_MODULE"):
    os.environ["DJANGO_SETTINGS_MODULE"] = "meiduo_mall.settings.dev"

# django初始化，加载django功能
django.setup()

if __name__ == '__main__':
    generate_static_index_html()
