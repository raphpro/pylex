# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 10:50:48 2019

@author: m79620
"""

import pandas as pd
from pylex import _config_file
from .tokenizer import Tokenizer

class PyLex(object):

    """
    PyLex is a lookup & evaluator of token expressions used by the Python lexical analyzer.
    See: https://docs.python.org/3/reference/lexical_analysis.

    Pylang tokens are predefined by the Python language,
        and are based on their own modified BNF notation.
    Thus, PyLex can function via using lookups for these exact tokens,
        rather than using a regex-based parser.
    However, PyLex could also be modified to evaluate via a regex parser.

    Users can instantiate PyLex() and type the name of the token they wish to lookup.
    PyLex will respond by providing the expression of the token's exact lexical definition.
    PyLex then evaluates that expression to its normal form,
        progressing through all sub-tokens,
        leaving no non-terminal lexical elements within the evaluated expression.

    Example:


    Configs are stored in PyLex_configs.xlsx.

    """



    print('PyLex is awesome')


    def __init__(self, config_file=_config_file, config_sheet_name="PyLex_configs"):
        """Instantiate an instance of the Pylex class.
        Call host_user(), which engages all PyLex methods on the instance."""

        self.df = pd.read_excel(config_file, config_sheet_name)

        self.master_list = []

        print('Welcome to PyLex')

        persistence = 'infinity'
        while persistence == 'infinity':
            self.host_user()
            decision = str(input('Would you like to search again? '))
            if decision == 'Yes' or decision == 'yes' or decision == 'Y' or decision == 'y':
                self.master_list.clear()
                continue
            else:
                print('\nThank you for using PyLex. Please visit again. :O)')
                self.master_list.clear()
                persistence = 0



    def host_user(self):
        """Host the user as a guest to PyLex. Offer an index of Python language tokens."""


        potential_pylang_token = self.input_token_name()

        expression = self.look_up_token(potential_pylang_token)
        evaluation = ''
        evaluation_attempt = 0

        if expression is not None:
            evaluation = self.evaluate_expression(expression, evaluation_attempt)
            while evaluation is not '':
                evaluation_attempt += 1
                print('')
                evaluation = self.evaluate_expression(evaluation, evaluation_attempt)
                continue

            print('\n\n{}\nNormal Form Evaluation: '.format(potential_pylang_token),\
                  *self.master_list, sep='')

        else:
            decision = input('Would you like to see an index of all Python language tokens? ')

            if decision == 'Yes' or decision == 'yes' or decision == 'Y' or decision == 'y':
#             index

                return self.df.token_name
            else:
                return 'No? ok.'


    def input_token_name(self):
        """Gather user input. User can enter the token they wish to evaluate."""

        user_input = input('Please enter the token you wish to look up: ')
        print('\n', end='')

        return user_input



    def look_up_token(self, input_token):
        """Look up the input token in the Pylang Token dataframe.
        Return None if token is not in Pylang Token dataframe."""

        lookup = self.df.expression_string[self.df.token_name == input_token].values
        lookup_result = lookup.item()    # convert to scalar & return
                #could also do result = lookup[0]

        if lookup_result is not None:
            expression = lookup_result[1:-1]
            print('Lexical Definition of {}: {}'.format(input_token, expression), end='\n\n')
            return expression
        else:
            print('The token name you have entered is not found '\
                      'in the list of tokens used by the Python lexical analyzer.')
            return



    def evaluate_expression(self, expression, eval_number):
        """Evaluate the entire expression"""

        print('\nEvaluation #{}'.format(eval_number))

        tokenizer = Tokenizer()
        token_seq = tokenizer.tokenize(expression)

        pylang_tokens_discovered_in_definition = []
        intermediate_definition_remainder = ''

        counter = 0

        for token in token_seq:    # List level
            for key in token:           # Dict level

                lexeme = token.get(key)

                if key == 'pylang_token':

                    pylang_tokens_discovered_in_definition.append(lexeme)
                    new_lexeme = self.look_up_token(lexeme)
                    intermediate_definition_remainder = intermediate_definition_remainder\
                                                        + new_lexeme
                    counter = 1
                    break

                elif counter == 1:
                    intermediate_definition_remainder = intermediate_definition_remainder + lexeme
                    break

                else:
                    self.master_list.append(lexeme)
                    token.clear()
                    break


#         print('Intermediate evaluation reveals the following Python Tokens: {}'\
#               .format(pylang_tokens_discovered_in_definition))

        print('intermediate definition of {}: '.format(expression),\
              *self.master_list, intermediate_definition_remainder)

#         print(intermediate_definition_remainder)

        return intermediate_definition_remainder


#      # Have input_token_name() print 'Token:'
# have express_lexical_definition_of_token() create a table titled 'Expressions'.
# Then have it print 'The following expression provides the lexical definition for the pylang
# token you have chosen:'