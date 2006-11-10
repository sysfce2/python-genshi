# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://genshi.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://genshi.edgewall.org/log/.

import doctest
import os
import shutil
import tempfile
import unittest

from genshi.template.loader import TemplateLoader
from genshi.template.markup import MarkupTemplate


class TemplateLoaderTestCase(unittest.TestCase):
    """Tests for the template loader."""

    def setUp(self):
        self.dirname = tempfile.mkdtemp(suffix='markup_test')

    def tearDown(self):
        shutil.rmtree(self.dirname)

    def test_search_path_empty(self):
        loader = TemplateLoader()
        self.assertEqual([], loader.search_path)

    def test_search_path_as_string(self):
        loader = TemplateLoader(self.dirname)
        self.assertEqual([self.dirname], loader.search_path)

    def test_relative_include_samedir(self):
        file1 = open(os.path.join(self.dirname, 'tmpl1.html'), 'w')
        try:
            file1.write("""<div>Included</div>""")
        finally:
            file1.close()

        file2 = open(os.path.join(self.dirname, 'tmpl2.html'), 'w')
        try:
            file2.write("""<html xmlns:xi="http://www.w3.org/2001/XInclude">
              <xi:include href="tmpl1.html" />
            </html>""")
        finally:
            file2.close()

        loader = TemplateLoader([self.dirname])
        tmpl = loader.load('tmpl2.html')
        self.assertEqual("""<html>
              <div>Included</div>
            </html>""", tmpl.generate().render())

    def test_relative_include_subdir(self):
        os.mkdir(os.path.join(self.dirname, 'sub'))
        file1 = open(os.path.join(self.dirname, 'sub', 'tmpl1.html'), 'w')
        try:
            file1.write("""<div>Included</div>""")
        finally:
            file1.close()

        file2 = open(os.path.join(self.dirname, 'tmpl2.html'), 'w')
        try:
            file2.write("""<html xmlns:xi="http://www.w3.org/2001/XInclude">
              <xi:include href="sub/tmpl1.html" />
            </html>""")
        finally:
            file2.close()

        loader = TemplateLoader([self.dirname])
        tmpl = loader.load('tmpl2.html')
        self.assertEqual("""<html>
              <div>Included</div>
            </html>""", tmpl.generate().render())

    def test_relative_include_parentdir(self):
        file1 = open(os.path.join(self.dirname, 'tmpl1.html'), 'w')
        try:
            file1.write("""<div>Included</div>""")
        finally:
            file1.close()

        os.mkdir(os.path.join(self.dirname, 'sub'))
        file2 = open(os.path.join(self.dirname, 'sub', 'tmpl2.html'), 'w')
        try:
            file2.write("""<html xmlns:xi="http://www.w3.org/2001/XInclude">
              <xi:include href="../tmpl1.html" />
            </html>""")
        finally:
            file2.close()

        loader = TemplateLoader([self.dirname])
        tmpl = loader.load('sub/tmpl2.html')
        self.assertEqual("""<html>
              <div>Included</div>
            </html>""", tmpl.generate().render())

    def test_relative_include_without_search_path(self):
        file1 = open(os.path.join(self.dirname, 'tmpl1.html'), 'w')
        try:
            file1.write("""<div>Included</div>""")
        finally:
            file1.close()

        file2 = open(os.path.join(self.dirname, 'tmpl2.html'), 'w')
        try:
            file2.write("""<html xmlns:xi="http://www.w3.org/2001/XInclude">
              <xi:include href="tmpl1.html" />
            </html>""")
        finally:
            file2.close()

        loader = TemplateLoader()
        tmpl = loader.load(os.path.join(self.dirname, 'tmpl2.html'))
        self.assertEqual("""<html>
              <div>Included</div>
            </html>""", tmpl.generate().render())

    def test_relative_include_without_search_path_nested(self):
        file1 = open(os.path.join(self.dirname, 'tmpl1.html'), 'w')
        try:
            file1.write("""<div>Included</div>""")
        finally:
            file1.close()

        file2 = open(os.path.join(self.dirname, 'tmpl2.html'), 'w')
        try:
            file2.write("""<div xmlns:xi="http://www.w3.org/2001/XInclude">
              <xi:include href="tmpl1.html" />
            </div>""")
        finally:
            file2.close()

        file3 = open(os.path.join(self.dirname, 'tmpl3.html'), 'w')
        try:
            file3.write("""<html xmlns:xi="http://www.w3.org/2001/XInclude">
              <xi:include href="tmpl2.html" />
            </html>""")
        finally:
            file3.close()

        loader = TemplateLoader()
        tmpl = loader.load(os.path.join(self.dirname, 'tmpl3.html'))
        self.assertEqual("""<html>
              <div>
              <div>Included</div>
            </div>
            </html>""", tmpl.generate().render())

    def test_relative_include_from_inmemory_template(self):
        file1 = open(os.path.join(self.dirname, 'tmpl1.html'), 'w')
        try:
            file1.write("""<div>Included</div>""")
        finally:
            file1.close()

        loader = TemplateLoader([self.dirname])
        tmpl2 = MarkupTemplate("""<html xmlns:xi="http://www.w3.org/2001/XInclude">
          <xi:include href="../tmpl1.html" />
        </html>""", filename='subdir/tmpl2.html', loader=loader)

        self.assertEqual("""<html>
          <div>Included</div>
        </html>""", tmpl2.generate().render())

    def test_load_with_default_encoding(self):
        f = open(os.path.join(self.dirname, 'tmpl.html'), 'w')
        try:
            f.write(u'<div>\xf6</div>'.encode('iso-8859-1'))
        finally:
            f.close()
        loader = TemplateLoader([self.dirname], default_encoding='iso-8859-1')
        loader.load('tmpl.html')

    def test_load_with_explicit_encoding(self):
        f = open(os.path.join(self.dirname, 'tmpl.html'), 'w')
        try:
            f.write(u'<div>\xf6</div>'.encode('iso-8859-1'))
        finally:
            f.close()
        loader = TemplateLoader([self.dirname], default_encoding='utf-8')
        loader.load('tmpl.html', encoding='iso-8859-1')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(TemplateLoader.__module__))
    suite.addTest(unittest.makeSuite(TemplateLoaderTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')