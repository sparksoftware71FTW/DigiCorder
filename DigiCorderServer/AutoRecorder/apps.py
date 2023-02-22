import os
import threading
import asyncio
import time
import json
from django.apps import AppConfig
from django.utils.timezone import timedelta
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from shapely import geometry
from fastkml import kml

"""
DOC STRING BLANK

"""

import logging
logger = logging.getLogger(__name__)


class AutoRecorderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AutoRecorder'

    def ready(self):

        from AutoRecorder import signals