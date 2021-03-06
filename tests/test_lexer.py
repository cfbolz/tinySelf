# -*- coding: utf-8 -*-
from rply import Token

from tinySelf.parser.lexer import lexer


def test_single_q_string():
    assert list(lexer.lex("'hello'")) == [
        Token('SINGLE_Q_STRING', "'hello'"),
    ]

    assert list(lexer.lex("'hello \\' quote'")) == [
        Token('SINGLE_Q_STRING', "'hello \\' quote'"),
    ]

    assert list(lexer.lex("'a \\' b' 'c \\' d'")) == [
        Token('SINGLE_Q_STRING', r"'a \' b'"),
        Token('SINGLE_Q_STRING', r"'c \' d'"),
    ]

    assert list(lexer.lex("'hello \n quote'")) == [
        Token('SINGLE_Q_STRING', "'hello \n quote'"),
    ]


def test_double_q_string():
    assert list(lexer.lex('"hello"')) == [
        Token('DOUBLE_Q_STRING', '"hello"'),
    ]

    assert list(lexer.lex('"hello \\" quote"')) == [
        Token('DOUBLE_Q_STRING', '"hello \\" quote"'),
    ]

    assert list(lexer.lex('"a \\" b" "c \\" d"')) == [
        Token('DOUBLE_Q_STRING', r'"a \" b"'),
        Token('DOUBLE_Q_STRING', r'"c \" d"'),
    ]

    assert list(lexer.lex('"hello \n quote"')) == [
        Token('DOUBLE_Q_STRING', '"hello \n quote"'),
    ]


def test_identifier():
    assert list(lexer.lex('identifier')) == [
        Token('IDENTIFIER', 'identifier'),
    ]

    assert list(lexer.lex('iDentIfier ID2')) == [
        Token('IDENTIFIER', 'iDentIfier'),
        Token('IDENTIFIER', 'ID2'),
    ]

    assert list(lexer.lex('p*')) == [
        Token('IDENTIFIER', 'p*'),
    ]



def test_argument():
    assert list(lexer.lex(':argument')) == [
        Token('ARGUMENT', ':argument'),
    ]

    assert list(lexer.lex('"string" :argument idenTifier')) == [
        Token('DOUBLE_Q_STRING', '"string"'),
        Token('ARGUMENT', ':argument'),
        Token('IDENTIFIER', 'idenTifier'),
    ]


def test_kw_identifier():
    assert list(lexer.lex('kwArgument: i')) == [
        Token('FIRST_KW', 'kwArgument:'),
        Token('IDENTIFIER', 'i'),
    ]


def test_kw():
    assert list(lexer.lex('kwArgument: i KeyWord: kw')) == [
        Token('FIRST_KW', 'kwArgument:'),
        Token('IDENTIFIER', 'i'),
        Token('KEYWORD', 'KeyWord:'),
        Token('IDENTIFIER', 'kw'),
    ]


def test_complex():
    assert list(lexer.lex('(kwArgument: i KeyWord: [id])')) == [
        Token('OBJ_START', '('),
        Token('FIRST_KW', 'kwArgument:'),
        Token('IDENTIFIER', 'i'),
        Token('KEYWORD', 'KeyWord:'),
        Token("BLOCK_START", '['),
        Token('IDENTIFIER', 'id'),
        Token("BLOCK_END", ']'),
        Token('OBJ_END', ')'),
    ]


def test_operator():
    assert list(lexer.lex('!')) == [
        Token('OPERATOR', '!'),
    ]

    assert list(lexer.lex('!@$%&*-+~/?<>,')) == [
        Token('OPERATOR', '!@$%&*-+~/?<>,')
    ]

    assert list(lexer.lex('! @ $ % & * - + ~ / ? < > ,')) == [
        Token('OPERATOR', '!'),
        Token('OPERATOR', '@'),
        Token('OPERATOR', '$'),
        Token('OPERATOR', '%'),
        Token('OPERATOR', '&'),
        Token('OPERATOR', '*'),
        Token('OPERATOR', '-'),
        Token('OPERATOR', '+'),
        Token('OPERATOR', '~'),
        Token('OPERATOR', '/'),
        Token('OPERATOR', '?'),
        Token('OPERATOR', '<'),
        Token('OPERATOR', '>'),
        Token('OPERATOR', ','),
    ]

    assert list(lexer.lex('==')) == [
        Token('OPERATOR', '==')
    ]

    assert list(lexer.lex('===')) == [
        Token('OPERATOR', '===')
    ]

def test_return():
    assert list(lexer.lex('^')) == [
        Token('RETURN', '^'),
    ]

    assert list(lexer.lex('^xe.')) == [
        Token('RETURN', '^'),
        Token('IDENTIFIER', 'xe'),
        Token('END_OF_EXPR', '.'),
    ]


def test_end_of_expression():
    assert list(lexer.lex('.')) == [
        Token('END_OF_EXPR', '.'),
    ]

    assert list(lexer.lex('obj message.')) == [
        Token('IDENTIFIER', 'obj'),
        Token('IDENTIFIER', 'message'),
        Token('END_OF_EXPR', '.'),
    ]


def test_separator():
    assert list(lexer.lex('|')) == [
        Token('SEPARATOR', '|'),
    ]

    assert list(lexer.lex('(|var| obj message.)')) == [
        Token('OBJ_START', '('),
        Token('SEPARATOR', '|'),
        Token('IDENTIFIER', 'var'),
        Token('SEPARATOR', '|'),
        Token('IDENTIFIER', 'obj'),
        Token('IDENTIFIER', 'message'),
        Token('END_OF_EXPR', '.'),
        Token('OBJ_END', ')'),

    ]


def test_comment():
    assert list(lexer.lex('#\n')) == [
        Token('COMMENT', '#\n'),
    ]

    assert list(lexer.lex('obj message. # comment \n id #')) == [
        Token('IDENTIFIER', 'obj'),
        Token('IDENTIFIER', 'message'),
        Token('END_OF_EXPR', '.'),
        Token('COMMENT', '# comment \n'),
        Token('IDENTIFIER', 'id'),
        Token('COMMENT', '#'),
    ]


def test_cascade():
    assert list(lexer.lex(';')) == [
        Token('CASCADE', ';'),
    ]

    assert list(lexer.lex('obj message; message2.')) == [
        Token('IDENTIFIER', 'obj'),
        Token('IDENTIFIER', 'message'),
        Token('CASCADE', ';'),
        Token('IDENTIFIER', 'message2'),
        Token('END_OF_EXPR', '.'),
    ]


def test_assingment_op():
    assert list(lexer.lex('=')) == [
        Token('ASSIGNMENT', '='),
    ]


def test_rw_assingment_op():
    assert list(lexer.lex('<-')) == [
        Token('RW_ASSIGNMENT', '<-'),
    ]


def test_self_keyword():
    assert list(lexer.lex('self')) == [
        Token('SELF', 'self'),
    ]
