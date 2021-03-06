from token import Token
from tokenizer import Tokenizer
import re

class SyntaxAnalysis:
    # grammar rules in a form of string:
    #   - @ denotes epsilon
    #   - . denotes empty item = error
    GRAMMAR = \
    " REQUIRED IMPLIED FIXED CDATA NMTOKEN IDREF ATTLIST ELEMENT EMPTY ANY PCDATA WORD , | \" ( ) < > ? * + $ NONE\n\
DTDOC . . . . . . . . . . . . . . . . . L;DECLARATION;< . . . . . .\n\
L . . . . . . . . . . . . . . . . . DTDOC . . . . @ .\n\
DECLARATION . . . . . . >;Z;WORD;ATTLIST >;X;WORD;ELEMENT . . . . . . . . . . . . . . . .\n\
X . . . . . . . . EMPTY ANY PCDATA . . . . );F;( . . . . . . . .\n\
F . . . . . . . . . . . . . . . Y;K;CP;( . . . . . . . .\n\
Y . . . . . . . . . . . . @ @ . . @ . . ? * + . .\n\
H . . . . . . . . . . . . H;CP;, . . . @ . . . . . . .\n\
K . . . . . . . . . . . . );H;CP;, );CP;| . . ) . . . . . . .\n\
CP . . . . . . . . . . . Y;WORD . . . Y;K;CP;( . . . . . . . .\n\
Z . . . . . . . . . . . Z;DEFAULTDECL;ATTRTYPE;WORD . . . . . . @ . . . . .\n\
ATTRTYPE . . . CDATA NMTOKEN IDREF . . . . . . . . . );E;WORD;( . . . . . . . .\n\
E . . . . . . . . . . . . . WORD;| . . @ . . . . . . .\n\
DEFAULTDECL REQUIRED IMPLIED \";B;WORD;\";J . . . . . . . . . . . \";B;WORD;\";J . . . . . . . . .\n\
J . . FIXED . . . . . . . . . . . @ . . . . . . . . .\n\
B . . . . . . . . . . . B;WORD . . @ . . . . . . . . .\n"

    # parse table structure:
    #      REQUIRED IMPLIED FIXED CDATA NMTOKEN IDREF ATTLIST ELEMENT EMPTY ANY PCDATA WORD , | \" ( ) < > ? * + $
    #   A
    #   B
    #   C
    #   D
    #   E
    #   F
    #   G
    #
    #   parse table is represented as a hash table of parse table row indexes
    #   (non terminals + terminals) where each of the hash values is another
    #   hash table with the column indexes as keys and set of terminas and
    #   nonterminals delimited by space for the given rule
    #
    PARSE_TABLE = {}
    ERROR_COUNT = 0

    def initializeParseTable(self):
        rows = filter(None,self.GRAMMAR.split('\n'))
        columns_indexes = filter(None,rows[0].split(' '))
        for row in rows[1:]:
            columns = row[0:].split(' ')
            self.PARSE_TABLE[columns[0]] = {}
            for idx, column in enumerate(columns[1:]):
                #print(columns[0], columns_indexes[idx], column)
                self.PARSE_TABLE[columns[0]][columns_indexes[idx]] = column


    def analyzeTokens(self, tokens):
        stack = []
        stack.append('$')
        stack.append('DTDOC')
        position = 0
        pop = stack[len(stack)-1]
        token = tokens[position]
        while pop is not "$":
            pop = stack[len(stack) - 1]
            print "\n--------------------"
            print "Stack: " + str(stack)
            print "Top of Stack: " + pop
            if type(token) == type(''):
                print "Token:\t" + str(token)
            else:
                print "Token:\t" + " value:" + str(token.value) + " type:" + str(token.type)
            print "--------------------\n"
            if tokens[position].type in {'SPECIAL', 'EOF'}:
                token = tokens[position].value
            else:
                token = tokens[position].type
            print("STACK: " + str(stack))
            print("TOP OF STACK: " + pop)
            print("TOKEN: " + tokens[position].type + " (" + tokens[position].value + ")")

            if pop not in self.PARSE_TABLE.keys() or pop is "$":
                if token == pop:
                    stack.pop()
                    position += 1
                    print("Top Of Stack equals Token, so we pop Top of Stack and move to another token.")
                elif pop == "@":
                    stack.pop()
                else:
                    print("***** ERROR: No match in Parse Table. *******")
                    self.ERROR_COUNT += 1
                    position, stack = self.recovery(tokens, position, stack)
            else:
                if self.PARSE_TABLE[pop][token] != ".":
                    rules = self.PARSE_TABLE[pop][token].split(';')
                    stack.pop()
                    print("Match found. Applying rules: " + pop + " -> " + self.printRules(rules))
                    for rule in rules:
                        stack.append(rule)
                else:
                    print("***** ERROR: No match in Parse Table. *******")
                    self.ERROR_COUNT += 1
                    position, stack = self.recovery(tokens, position, stack)

        print("\nDONE")
        print("\t" + str(self.ERROR_COUNT) + " errors found.")

    def recovery(self, tokens, position, stack):
        print("***** RECOVERY:")
        print("Skipping tokens:")
        while tokens[position].value != ">" and tokens[position].value != "<":
            position += 1
            print("\t" + tokens[position].value)
        if tokens[position].value != "<":
            position += 1

        print("Poping out of stack:")
        topOfStack = stack[len(stack)-1]
        while topOfStack != 'L':
            print("\t'" + stack.pop())
            topOfStack = stack[len(stack) - 1]

        return position, stack

    def printRules(self, rules):
        line = ""
        for rule in reversed(rules):
            line  = line + " " + rule
        return line
