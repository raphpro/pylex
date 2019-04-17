# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 10:50:01 2019

@author: Raphael David
"""

import pandas as pd
from pylex import _config_file
from .lexer import Lexer

class Tokenizer(object):


    """
    Tokenizer is a tokenizer: it produces tokens.

    Called by:       a parser
    Initial Input:   strings
    Calls:           a lexer
    Secondary Input: lexemes
    Output:          tokens

    Tokenizer receives a string from a parser and sends that string as input to a lexer.
    It then reads that lexer's output as lexemes.
    Tokenizer is currently set to work with the specific lexer in this module, Lexer.
    However, it could easily be recalibrated to work with any other specific lexer.

    Once Tokenizer receives lexemes from a lexer,
        it then categorizes the lexemes into key-value pairs.
    Each key-value pair constitutes 1 token.

    Tokenizer outputs all resulting tokens together as a single list of dictionaries.
    Each individual dictionary constitutes 1 token.

    """



    print('Tokenizer reporting for duty')


    def __init__(self, config_file=_config_file,\
                 tokenizer_config_sheet_name="Tokenizer_configs",\
                pylex_config_sheet_name="PyLex_configs"):
        """Instantiate an instance of the Tokenizer class."""

#         subtoken_seq = []
#         token_seq = []


        self.tokenizer_df = pd.read_excel(config_file, tokenizer_config_sheet_name)
        self.pylex_df = pd.read_excel(config_file, pylex_config_sheet_name)

        self.subtoken_configs = self.tokenizer_df.operator.values
        self.operator_configs = self.tokenizer_df.operator_name.values
        self.phrase_configs = self.tokenizer_df.phrase_name.values
        self.token_configs = self.pylex_df.token_name.values


    def tokenize(self, expression):
        """
        Call Lexer to lex a str expression.
        Feed the list of resulting lexemes through all other Tokenizer methods.

        Input: str
        Output: list of tokens
        """

        string_to_be_lexed = Lexer()
        lexeme_list = string_to_be_lexed.lex_string(expression)

        subtoken_seq = self.identify_subtokens(lexeme_list)
        token_seq = self.identify_token_phrases(subtoken_seq)
#         print('Token Seq = ', token_seq)
        token_seq = self.identify_pylang_tokens(token_seq)

#         print('Tokens: {}'.format(token_seq))
        return token_seq


    def identify_subtokens(self, lexeme_list):
        """
        Assign each lexeme as a value to keys that are based on a pre-determined category list.
        Return the key-value pairs as separate dict objects within a list.
        Each dict should hold only one key-value pair.

        Input: list of lexemes
        Output: list of subtokens
        """

        subtoken_seq = []

        for lexeme in lexeme_list:
            lookup = '"' + lexeme + '"'

            if lookup in self.subtoken_configs:
                lookup_result = self.tokenizer_df.operator_name\
                                [self.tokenizer_df.operator == lookup].values

                key = lookup_result.item()   # The name of the operator

                subtoken_seq.append({key: lexeme})

            else:
                subtoken_seq.append({'potential_pylang_token': lexeme})

#         print('Subtoken Seq = ', subtoken_seq, end='\n\n')
        return subtoken_seq


#  make the white space a separator i/o operator



    def identify_token_phrases(self, subtoken_seq):
        """
        Combine certain subtokens into larger token phrases
            so that they can be glossed over by a parser and not reparsed a second time.
        Phrases are controlled by config. Each phrase constitutes 1 token.
        Python language tokens group the following items together as phrases:
            items between angle brackets &
            items between a phrase_closering set of quotes.
        These items will never become a pylang token.
        """

        token_seq = []
#         print('beg:', token_seq)

        lookup = ''
        token = ''
        lexeme = ''
        match = ''
        mode = 'proceed'

        for subtoken in subtoken_seq:    # List level
            for key in subtoken:           # Dict level

                lexeme = lexeme + subtoken.get(key)
#                 print('lexeme =', lexeme)

                if mode == 'hold for phrase':
#                     print('holding')

                    if str(key) == str(match):
#                         print('key does equal match')
                        lookup = self.tokenizer_df.phrase_name\
                            [self.tokenizer_df.operator_name == key].values
                        phrase = lookup.item()
#                         print('phrase =', phrase)

                        token = {str(phrase): lexeme}
                        token_seq.append(token)
#                         print('Token Seq: ', token_seq)
                        lexeme = ''
                        mode = 'proceed'
                        break

                    else:
                        break

                else:
                    lookup = self.tokenizer_df.phrase_opener\
                            [self.tokenizer_df.operator_name == key].values
#                     print('kv = ', subtoken)
#                     print('key = ', key)
#                     print('lookup = ', lookup)
                    is_a_phrase = lookup.item()
#                     print('Phrase?', is_a_phrase)
#                     print(type(is_a_phrase))

                    if is_a_phrase:
#                         print('made it to IF')
                        lookup = self.tokenizer_df.phrase_closer\
                                [self.tokenizer_df.operator_name == key].values
#                         print('since True, lookup =', lookup)
                        match = lookup.item()
#                         print('match =', match)
                        mode = 'hold for phrase'
                        break

                    else:
                        token = {key: lexeme}
                        token_seq.append(token)
                        lexeme = ''
                        break

        else:
            if mode != 'proceed':
                token = {'Syntax Error': lexeme}
                token_seq.append(token)
                return token_seq
            else:
                return token_seq


    def identify_pylang_tokens(self, token_seq):
        """
        Read a list of tokens.
        Determine whether a potential Python language token (pylang token)
            does indeed qualify as a pylang token.
        Return the same list of tokens, but change the names of the keys for pylang tokens.
        """

        final_token_seq = []

        for token in token_seq:    # List level
            for key in token:           # Dict level

                if key == 'potential_pylang_token':
#                     print('POTENTIAL!')
                    lexeme = token.get(key)
#                     print(lexeme)
#                     print(self.token_configs)

                    if lexeme in self.token_configs:
                        pylang_token = {'pylang_token': lexeme}  # If pylang, rekey as pylang.
                        final_token_seq.append(pylang_token)
                    else:            # If potential is not pylang, rekey as 'definition extra'.
                        final_token = {'definition_extras': lexeme}
                        final_token_seq.append(final_token)

                else:
                    final_token_seq.append(token)    # If not potential, keep the token as-is.

        return final_token_seq
