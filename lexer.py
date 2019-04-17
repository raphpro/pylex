# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 10:45:57 2019

@author: Raphael David
"""
import pandas as pd
from pylex import _config_file

class Lexer(object):

    """
    Lexer is a lexical analyzer, or lexer.
    It turns strings into lexemes and its methods can be called by a tokenizer.

    Called by: a tokenizer
    Input:     strings
    Output:    lexemes

    This lexer (Lexer) is written specifically for reading the fundamental language tokens
        of the Python programming language,
        all of which are built on a modified BNF grammar notation.
            Please see: https://docs.python.org/3.7/reference/introduction.html#notation
    Thus, Lexer is not designed to read traditional regexes,
        but could be modified to do so.

    Lexer can be configured by a user via config file.
    Config contains a pre-defined delimiter list, and a pre-defined list of seqs.


    Lexer consists of a control method (lex_string()) and 2 main processors:

        Isolating Scanner - (isolate_priority_lexemes()):
            Takes in an input dictionary value (always a string) and
                identifies sequences of chars within that string
                that match sequences designated by a config file available to the user.
            It then isolates these sequences as priority sequences
                to prevent them from being sent to the slicing scanner.
            An instance var master sequence is used to hold all sequences of chars,
                both those that are priorities and those that are not.
            The master sequence is read by the control method (lex_string()).
            lex_string() sends the priority sequences directly to an output list of lexemes
                and sends the none-priority sequences to the slicing scanner
                which ultimately also sends its results to the lexeme list.
            Each element of the lexeme list constitutes 1 lexeme.

        Slicing/Processing Scanner - (process_string()):
            Scans each char of an input string (read from an input dict)
                to identify delimiter chars.
            During the scan, contiguous non-delimiter chars are combined with each other
                until a delimiter is reached.
            Once a delimiter char is identified,
                the group of these contiguous chars (not including the delimiter) is assigned,
                as a whole, to be one string element of the final output list of lexemes.
            The delimiter is then isolated and assigned as a string element
                of the same lexeme list.
            Scanning resumes and this same process is repeated until the lexeme list has been
                supplied with all
                isolated delimiter string elements
                & contiguous non-delimiter string elements,
                each as separate lexemes.

        The slicing scanner scans & slices by individual delimiter chars.
        However, since some delimiters have the potential to be members of larger sequences--
            sequences that need to be kept together to form specific pre-defined lexemes--
            a method is needed to prevent certain sequences from being sliced.
        Hence, the method: isolate_priority_lexemes().


    Example:

        1. var some_string = 'abc....123.z'

        2. some_string is input as an arg to lex_string().
        lex_string() converts the string into the value of a key-value pair in dict format.
        It then sends some_string_value to isolate_priority_lexemes().

        3. Config file designates an ellipsis '...' as a priority.

        4. some_string_value is scanned by isolate_priority_lexemes() for priority sequences.
        isolate_priority_lexemes() segregates ellipses away from the rest of the chars
            and fills up empty instance var master_seq with the segregated sequences.
        master_seq is a list of dicts, each with only 1 key-value pair.
        Priority sequences are keyed as 'lexeme'.
        All other char sequences are keyed as 'string'.
        master_seq = [{'string': 'abc'}, {'lexeme': '...'}, {'string': '.123.z'}]

        5. lex_string() reads keys in master_seq in order.
        'lexeme' keyed values are sent to a final lexeme list var lexeme_seq.
        'string' keyed values are sent to process_string()
            and the results are sent to lexeme_seq.

        6. Config file designates '.' as a delimiter.

        7. process_string() reads the 'string' keyed value: '.123.z'.
        The value is sliced based on configured delimiters.
        Output: ['.', '123', '.', 'z']

        8. lex_string() returns the final list lexeme_seq.
        Output: lexemes_seq: ['abc', '...', '.', '123', '.', 'z']

        The lexemes in lexeme_seq can now be tokenized by a tokenizer.

    """



    print('Lexer reporting for duty')


    def __init__(self, config_file=_config_file, config_sheet_name="Lexer_configs"):
        """Instantiate an instance of the Lexer class."""

        self.master_seq = []

        self.df = pd.read_excel(config_file, config_sheet_name)

        self.delimiter_configs = self.df.delimiter.values

        # Select the number of rows in the config file that contain priority lexemes.
        self.config_row_count_priority_seq_chars = 2



    def lex_string(self, input_string):
        """Call all Lexer methods to lex an input string. Output the resulting lexeme list.
            1. Isolate & extract priority lexemes (identified by config file)
                out from the input string so as not to be included in the slicing scanner.
            2. Scan & slice the remaining portions of the input string
                based on delimiters specified by config file.
        Input: str
        Output: list of lexemes
        """


        # Isolate & extract:

        intermediate_seq = [{'string': input_string}]

        while len(intermediate_seq) != 0:
            intermediate_seq = self.isolate_priority_lexemes(intermediate_seq)
            continue


        # Scan & slice:

        lexemes = []

        for element in self.master_seq:
            for key in element:
                if key == 'lexeme':
                    lexemes.append(str(element.get(key)))
                else:
                    for result in self.process_string(str(element.get(key))):
                        lexemes.append(result)
        else:
#             print('\nLexemes: ', lexemes, end = '\n\n\n')
            self.master_seq.clear()
            return lexemes



    def isolate_priority_lexemes(self, intermediate_seq):
        """
        Isolate certain char sequences to prevent them from being included elsewhere.
        These 'priority' sequences are ranked such that the top row in the config file
            is considered first before all others, the second considered second, etc.
        Thus, the user can prioritize which sequences are higher in priority.

        Input: list of dicts
        Output: list of dicts

        """
        pair = intermediate_seq[0]  # Key-value pair
        for key in pair:    # List level
            if key == 'lexeme':
                self.master_seq.append(intermediate_seq.pop(0))
                return intermediate_seq
            for char_seq in self.df.priority_char_seqs.values[0:1]:  # Row in config file
                lookup = char_seq[1:-1]
                if lookup in pair.get(key):
                    i = pair.get(key).index(lookup)  # index where the seq starts
                    j = i + len(lookup)              # index immediately after the seq
                    if i == 0:
                        intermediate_seq[0] = {'lexeme': lookup}
                        intermediate_seq.insert(1, {'string': pair.get(key)[j:]})
                        return intermediate_seq
                    else:
                        intermediate_seq[0] = {'string': pair.get(key)[0:i]}
                        intermediate_seq.insert(1, {'lexeme': lookup})
                        intermediate_seq.insert(2, {'string': pair.get(key)[j:]})
                        return intermediate_seq

                else:           # If config not found then...
                    continue        # Continue to cycle thru the priority list

            else:
                self.master_seq.append(intermediate_seq.pop(0))
                return intermediate_seq


    def process_string(self, input_string):

        """
        Scan an input string and slice it char by char.
        Isolate chars that are part of the supplied delimiter_list
            and segregate them as individual lexeme candidates.
        Cluster the remaining chars into groups called lexemes, delimited by the delimiters.
        Output a list containing each segregated lexeme in order.

        Input: str
        Output: list of lexemes
        """

        lexeme_seq = []

        lexeme = ''

        for char in input_string:
            item = '"' + char + '"'

            if item not in self.delimiter_configs:
                lexeme = str(lexeme) + char
                continue

            else:
                if len(lexeme) > 0:
                    lexeme_seq.append(lexeme)
                lexeme = ''
                lexeme_seq.append(char)
                continue

        if len(lexeme) > 0:
            lexeme_seq.append(lexeme)

        return lexeme_seq
