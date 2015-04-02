from __future__ import absolute_import

from celery import shared_task


@shared_task
def add_new_user(user):
    from neuf_userinfo.utils import add_new_user_sync
    add_new_user_sync(user)