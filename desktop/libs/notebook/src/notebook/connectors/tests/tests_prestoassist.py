#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from nose.tools import assert_equal
import mock
from mock import ANY

from notebook.connectors.jdbc import Assist, PrestoAssist, JdbcApi

from django.contrib.auth.models import User
from desktop.lib.django_test_util import make_logged_in_client

class TestPrestoAssist(object):

	def setUp(self):
		self.presto_assist = PrestoAssist(DummyDb())
		self.test_db = "test_db"
		self.test_tbl = "test_tbl"
		self.test_col = ["test_col", "varchar", "", "test_comment"]

		self.client = make_logged_in_client(username="test", groupname="test", recreate=False, is_superuser=False)
		self.user = User.objects.get(username='test')

	@mock.patch('notebook.connectors.jdbc.query_and_fetch')
	def test_get_databases(self, mock_query_and_fetch):
		mock_query_and_fetch.return_value = [[self.test_db]], None
		expected = [self.test_db]
		assert_equal(expected, self.presto_assist.get_databases())
		mock_query_and_fetch.assert_called_with(ANY, 'SHOW SCHEMAS')

	@mock.patch('notebook.connectors.jdbc.query_and_fetch')
	def test_get_tables(self, mock_query_and_fetch):
		mock_query_and_fetch.return_value = [[self.test_tbl]], None
		expected = [{'type': 'Table', 'name':self.test_tbl}]
		assert_equal(expected, self.presto_assist.get_tables(self.test_db, [self.test_tbl]))
		mock_query_and_fetch.assert_called_with(ANY, 'SHOW TABLES FROM %s' % self.test_db)

	@mock.patch('notebook.connectors.jdbc.query_and_fetch')
	def test_get_columns(self, mock_query_and_fetch):
		mock_query_and_fetch.return_value = [self.test_col], None
		expected = [[self.test_col[0], self.test_col[1], '', '', '', self.test_col[3]]]
		assert_equal(expected, self.presto_assist.get_columns(self.test_db, self.test_tbl))
		mock_query_and_fetch.assert_called_with(ANY, 'SHOW COLUMNS FROM %s.%s' % (self.test_db, self.test_tbl))

	def test_get_assist_presto(self):
		jdbc = JdbcApi(self.user, {'name':'presto', 'options':{'driver':'com.facebook.presto.jdbc.PrestoDriver'}})
		assert_equal(PrestoAssist, jdbc._get_assist().__class__)

	def test_get_assist_jdbc(self):
		jdbc = JdbcApi(self.user, {'name':'mysql', 'options':{'driver':'com.mysql.jdbc.Driver'}})
		assert_equal(Assist, jdbc._get_assist().__class__)

class DummyDb(): pass
