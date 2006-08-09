# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://markup.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://markup.edgewall.org/log/.

import doctest
import unittest

from markup.input import XML
from markup.path import Path, PathSyntaxError


class PathTestCase(unittest.TestCase):

    def test_error_no_absolute_path(self):
        self.assertRaises(PathSyntaxError, Path, '/root')

    def test_error_unsupported_axis(self):
        self.assertRaises(PathSyntaxError, Path, '..')
        self.assertRaises(PathSyntaxError, Path, 'parent::ma')

    def test_1step(self):
        xml = XML('<root><elem/></root>')

        path = Path('elem')
        self.assertEqual('<Path "descendant::elem">', repr(path))
        self.assertEqual('<elem/>', path.select(xml).render())

        path = Path('child::elem')
        self.assertEqual('<Path "child::elem">', repr(path))
        self.assertEqual('<elem/>', path.select(xml).render())

        path = Path('//elem')
        self.assertEqual('<Path "descendant-or-self::node()/child::elem">',
                         repr(path))
        self.assertEqual('<elem/>', path.select(xml).render())

        path = Path('descendant::elem')
        self.assertEqual('<Path "descendant::elem">', repr(path))
        self.assertEqual('<elem/>', path.select(xml).render())

    def test_1step_self(self):
        xml = XML('<root><elem/></root>')

        path = Path('.')
        self.assertEqual('<Path "self::node()">', repr(path))
        self.assertEqual('<root><elem/></root>', path.select(xml).render())

        path = Path('self::node()')
        self.assertEqual('<Path "self::node()">', repr(path))
        self.assertEqual('<root><elem/></root>', path.select(xml).render())

    def test_1step_wildcard(self):
        xml = XML('<root><elem/></root>')

        path = Path('*')
        self.assertEqual('<Path "descendant::*">', repr(path))
        self.assertEqual('<elem/>', path.select(xml).render())

        path = Path('child::*')
        self.assertEqual('<Path "child::*">', repr(path))
        self.assertEqual('<elem/>', path.select(xml).render())

        path = Path('child::node()')
        self.assertEqual('<Path "child::node()">', repr(path))
        self.assertEqual('<elem/>', Path('child::node()').select(xml).render())

        path = Path('//*')
        self.assertEqual('<Path "descendant-or-self::node()/child::*">',
                         repr(path))
        self.assertEqual('<elem/>', path.select(xml).render())

    def test_1step_attribute(self):
        path = Path('@foo')
        self.assertEqual('<Path "attribute::foo">', repr(path))
        self.assertEqual('', path.select(XML('<root/>')).render())

        xml = XML('<root foo="bar"/>')
        self.assertEqual('bar', path.select(xml).render())

        path = Path('./@foo')
        self.assertEqual('<Path "self::node()/attribute::foo">', repr(path))
        self.assertEqual('bar', Path('./@foo').select(xml).render())

    def test_1step_text(self):
        xml = XML('<root>Hey</root>')

        path = Path('text()')
        self.assertEqual('<Path "descendant::text()">', repr(path))
        self.assertEqual('Hey', path.select(xml).render())

        path = Path('./text()')
        self.assertEqual('<Path "self::node()/child::text()">', repr(path))
        self.assertEqual('Hey', path.select(xml).render())

        path = Path('//text()')
        self.assertEqual('<Path "descendant-or-self::node()/child::text()">',
                         repr(path))
        self.assertEqual('Hey', path.select(xml).render())

        path = Path('.//text()')
        self.assertEqual('<Path "self::node()/child::text()">', repr(path))
        self.assertEqual('Hey', path.select(xml).render())

    def test_2step(self):
        xml = XML('<root><foo/><bar/></root>')
        self.assertEqual('<foo/><bar/>', Path('*').select(xml).render())
        self.assertEqual('<bar/>', Path('bar').select(xml).render())
        self.assertEqual('', Path('baz').select(xml).render())

    def test_2step_complex(self):
        xml = XML('<root><foo><bar/></foo></root>')

        path = Path('foo/bar')
        self.assertEqual('<Path "descendant::foo/child::bar">', repr(path))
        self.assertEqual('<bar/>', path.select(xml).render())

        path = Path('foo/*')
        self.assertEqual('<Path "descendant::foo/child::*">', repr(path))
        self.assertEqual('<bar/>', path.select(xml).render())

        xml = XML('<root><foo><bar id="1"/></foo><bar id="2"/></root>')
        self.assertEqual('<bar id="1"/><bar id="2"/>',
                         Path('bar').select(xml).render())

    def test_2step_text(self):
        xml = XML('<root><item>Foo</item></root>')

        path = Path('item/text()')
        self.assertEqual('<Path "descendant::item/child::text()">', repr(path))
        self.assertEqual('Foo', path.select(xml).render())

        path = Path('*/text()')
        self.assertEqual('<Path "descendant::*/child::text()">', repr(path))
        self.assertEqual('Foo', path.select(xml).render())

        path = Path('//text()')
        self.assertEqual('<Path "descendant-or-self::node()/child::text()">',
                         repr(path))
        self.assertEqual('Foo', path.select(xml).render())

        xml = XML('<root><item>Foo</item><item>Bar</item></root>')
        self.assertEqual('FooBar', Path('item/text()').select(xml).render())

    def test_3step(self):
        xml = XML('<root><foo><bar/></foo></root>')
        path = Path('root/foo/*')
        self.assertEqual('<Path "descendant::root/child::foo/child::*">',
                         repr(path))
        self.assertEqual('<bar/>', path.select(xml).render())

    def test_3step_complex(self):
        xml = XML('<root><foo><bar/></foo></root>')
        path = Path('*/bar')
        self.assertEqual('<Path "descendant::*/child::bar">', repr(path))
        self.assertEqual('<bar/>', path.select(xml).render())

        xml = XML('<root><foo><bar id="1"/></foo><bar id="2"/></root>')
        path = Path('//bar')
        self.assertEqual('<Path "descendant-or-self::node()/child::bar">',
                         repr(path))
        self.assertEqual('<bar id="1"/><bar id="2"/>',
                         path.select(xml).render())

    def test_node_type_comment(self):
        xml = XML('<root><!-- commented --></root>')
        path = Path('comment()')
        self.assertEqual('<Path "descendant::comment()">', repr(path))
        self.assertEqual('<!-- commented -->', path.select(xml).render())

    def test_node_type_text(self):
        xml = XML('<root>Some text <br/>in here.</root>')
        path = Path('text()')
        self.assertEqual('<Path "descendant::text()">', repr(path))
        self.assertEqual('Some text in here.', path.select(xml).render())

    def test_node_type_node(self):
        xml = XML('<root>Some text <br/>in here.</root>')
        path = Path('node()')
        self.assertEqual('<Path "descendant::node()">', repr(path))
        self.assertEqual('Some text <br/>in here.', path.select(xml).render())

    def test_node_type_processing_instruction(self):
        xml = XML('<?python x = 2 * 3 ?><root><?php echo("x") ?></root>')

        path = Path('processing-instruction()')
        self.assertEqual('<Path "descendant::processing-instruction()">',
                         repr(path))
        self.assertEqual('<?python x = 2 * 3 ?><?php echo("x") ?>',
                         path.select(xml).render())

        path = Path('processing-instruction("php")')
        self.assertEqual('<Path "descendant::processing-instruction(\"php\")">',
                         repr(path))
        self.assertEqual('<?php echo("x") ?>', path.select(xml).render())

    def test_simple_union(self):
        xml = XML('<root>Oh <foo>my</foo></root>')
        path = Path('*|text()')
        self.assertEqual('<Path "descendant::*|descendant::text()">',
                         repr(path))
        self.assertEqual('Oh <foo>my</foo>', path.select(xml).render())

    def test_predicate_name(self):
        xml = XML('<root><foo/><bar/></root>')
        self.assertEqual('<foo/>',
                         Path('*[name()="foo"]').select(xml).render())

    def test_predicate_localname(self):
        xml = XML('<root><foo xmlns="NS"/><bar/></root>')
        self.assertEqual('<foo xmlns="NS"/>',
                         Path('*[local-name()="foo"]').select(xml).render())

    def test_predicate_namespace(self):
        xml = XML('<root><foo xmlns="NS"/><bar/></root>')
        self.assertEqual('<foo xmlns="NS"/>',
                         Path('*[namespace-uri()="NS"]').select(xml).render())

    def test_predicate_not_name(self):
        xml = XML('<root><foo/><bar/></root>')
        self.assertEqual('<bar/>',
                         Path('*[not(name()="foo")]').select(xml).render())

    def test_predicate_attr(self):
        xml = XML('<root><item/><item important="very"/></root>')
        self.assertEqual('<item important="very"/>',
                         Path('root/item[@important]').select(xml).render())
        self.assertEqual('<item important="very"/>',
                         Path('root/item[@important="very"]').select(xml).render())

    def test_predicate_attr_equality(self):
        xml = XML('<root><item/><item important="notso"/></root>')
        self.assertEqual('',
                         Path('root/item[@important="very"]').select(xml).render())
        self.assertEqual('<item/><item important="notso"/>',
                         Path('root/item[@important!="very"]').select(xml).render())

    def test_predicate_attr_and(self):
        xml = XML('<root><item/><item important="very"/></root>')
        path = Path('root/item[@important and @important="very"]')
        self.assertEqual('<item important="very"/>', path.select(xml).render())
        path = Path('root/item[@important and @important="notso"]')
        self.assertEqual('', path.select(xml).render())

    def test_predicate_attr_or(self):
        xml = XML('<root><item/><item important="very"/></root>')
        path = Path('root/item[@urgent or @important]')
        self.assertEqual('<item important="very"/>', path.select(xml).render())
        path = Path('root/item[@urgent or @notso]')
        self.assertEqual('', path.select(xml).render())


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(Path.__module__))
    suite.addTest(unittest.makeSuite(PathTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
