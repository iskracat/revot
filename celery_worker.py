#!/usr/bin/env python
import os
from revot import celery, create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()
