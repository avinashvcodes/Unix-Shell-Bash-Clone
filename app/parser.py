operators = {"|", "&&", "||"}
redirects = {">", ">>", "1>", "1>>", "2>", "2>>"}

from tokenizer import tokenize

class Operator:

    def __init__(self, op):
        self.op = op
    
    def __repr__(self):
        return f"Operator({self.op})"

class SubShell:

    def __init__(self, arguments):
        self.arguments = arguments
        self.ast = None
        self.redirect = []

    def parse(self):
        if self.ast is None:
            self.ast = parser(self.arguments, 0, len(self.arguments))
    
    def set_redirect(self, redirect, file):
        self.redirect.append((redirect, file))
    
    def __repr__(self):
        return f"SubShell({self.arguments})"

class Command:

    def __init__(self, cmd: list):
        self.cmd: list = cmd
        self.redirect = []
    
    def set_redirect(self, redirect, file):
        self.redirect.append((redirect, file))

    def __repr__(self):
        return f"Command({' '.join(self.cmd)})"

class LogicalAND:

    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

class LogicalOR:

    def __init__(self, left, right):
        self.left = left
        self.right = right

class Pipe:

    def __init__(self):
        self.cmds = []
    
    def add_cmd(self, cmd):
        self.cmds.append(cmd)
    
    def complete(self, tokens, start):
        cur = start
        while tokens[cur+1] not in operators:
            cur+=1

def get_token_sequence(tokens, l, r):
    cmd_cur = l
    while cmd_cur < r and tokens[cmd_cur] not in operators and tokens[cmd_cur] not in redirects:
        cmd_cur+=1
    cmd_start = l
    cmd_end = cmd_cur
    return tokens[cmd_start:cmd_end], cmd_cur

def token_grouper(tokens, l=0, r:int|None = None):
    if r is None:
        r = len(tokens)

    grouped_tokens = []

    while l < r:
        if tokens[l] == "(":
            open_ = 1
            cur = l+1
            while cur < r and open_ != 0:
                if tokens[cur] == ")":
                    open_-=1
                if tokens[cur] == "(":
                    open_+=1
                cur+=1
            if open_ != 0:
                raise Exception("Unmatched parentheses")
            grouped_tokens.append(SubShell(token_grouper(tokens, l+1, cur-1)))
            l = cur
        elif tokens[l] in redirects:
            cmd = grouped_tokens[-1]
            if isinstance(cmd, Command) or isinstance(cmd, SubShell):
                redirect = tokens[l]
                l+=1
                token_sequence, l = get_token_sequence(tokens, l, r)
                if not token_sequence:
                    raise Exception("Missing file for redirect")
                cmd.set_redirect(redirect, token_sequence[0])
            else:
                raise Exception("Redirect without command")
        elif tokens[l] in operators:
            grouped_tokens.append(Operator(tokens[l]))
            l+=1
        else:
            token_sequence, l = get_token_sequence(tokens, l, r)
            grouped_tokens.append(Command(token_sequence))
    
    return grouped_tokens
            
print(token_grouper(tokenize("(cat file.txt | grep err) | wc > out.txt && echo done")))

op_mapping = {
    "||": LogicalOR,
    "&&": LogicalAND,
    "|": Pipe
}

operator_precedence = {
    "||": 10,
    "&&": 20,
    "|": 30
}


def parser(grouped_tokens, l, r):

    precedence = None
    index = None
    op = None

    for i in range(l, r):
        token = grouped_tokens[i]
        if not isinstance(token, Operator):
            continue

        if precedence is None or precedence >= operator_precedence[token.op]:
            precedence = operator_precedence[token.op]
            index = i
            op = token.op

    if index is None:
        node = grouped_tokens[l]
        if isinstance(node, SubShell):
            node.parse()
        return node
    
    if op == "|":
        pipe = Pipe()

        current = []
        for i in range(l, r):
            token = grouped_tokens[i]

            if isinstance(token, Operator) and token.op == "|":
                pipe.add_cmd(parser(current, 0, len(current)))
                current = []
            else:
                current.append(token)

        if current:
            pipe.add_cmd(parser(current, 0, len(current)))

        return pipe
    
    node = op_mapping[op]()

    node.left = parser(grouped_tokens, l, index)
    node.right = parser(grouped_tokens, index+1, r)

    return node

    
    