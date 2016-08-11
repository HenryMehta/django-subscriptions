import os

__version__ = '0.0.1'

# Subscriptions static directory
SUBSCRIPTIONS_STATIC_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'static_dir/subscriptions')

# Name used in Stripe payment and on emails
SUBSCRIPTIONS_SITE_NAME = "MySite.com"