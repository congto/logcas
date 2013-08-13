from datetime import datetime
from datetime import timedelta
import json
import unittest

from bson.objectid import ObjectId
from flask import url_for
from flask.ext import testing
from flask.ext import pymongo

import logcas.bootstrap
import db

DATA = []


class ArchivedLogShowTestCase(testing.TestCase):

    def create_app(self):
        app = logcas.bootstrap.app
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        return app

    @classmethod
    def setUpClass(cls):
        global DATA
        now = datetime.today()
        cls.now = now
        onesecond = timedelta(0, 1)
        for i in range(0, 20):
            for level in logcas.bootstrap.LEVELMAP.keys():
                data = db.archived_logs.save({
                    "time": now,
                    "created": int(now.strftime("%s")),
                    "message": "This is a message",
                    "hostname": "localhost",
                    "levelno": level,
                    "levelname": logcas.bootstrap.LEVELMAP[level],
                    "binary": "nova-compute",
                    "extra": {
                        "request_id": str(i),
                        "remote_address": "127.0.0.1",
                        "project_name": "testproject",
                        "user_name": "testuser",
                        "user_id": "xxxxxxxx",
                    }
                })
                now = now + onesecond
                DATA.append(data)

    @classmethod
    def tearDownClass(cls):
        db.archived_logs.drop()

    def test_with_saved_entries(self):
        response = self.client.get(url_for('_archived_log_show',
                                           log_id=DATA[0]))
        self.assert200(response)
        self.assertTemplateUsed('archived_log_show.html')

    # no param

    def test_without_params(self):
        response = self.client.get(url_for('_archived_log_show',
                                           log_id=ObjectId()))
        self.assert404(response)

    # style

    def test_with_style_(self):
        response = self.client.get(url_for('_archived_log_show',
                                           log_id=DATA[0], style=""))
        self.assert400(response)

    def test_with_style_abc(self):
        response = self.client.get(url_for('_archived_log_show',
                                           log_id=DATA[0], style="abc"))
        self.assert400(response)

    def test_with_style_default(self):
        response = self.client.get(url_for('_archived_log_show',
                                           log_id=DATA[0], style="default"))
        self.assert200(response)
        self.assertTemplateUsed('archived_log_show.html')

    def test_with_style_dark(self):
        response = self.client.get(url_for('_archived_log_show',
                                           log_id=DATA[0], style="dark"))
        self.assert200(response)
        self.assertTemplateUsed('archived_log_show.html')


if __name__ == '__main__':
    unittest.main()
