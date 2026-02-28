operators = {"|", "&&", "||", ">", ">>", "1>", "1>>"}
redirects = {">", ">>", "1>", "1>>"}

from tokenizer import tokenize

class Operator:

    def __init__(self, op):
        self.op = op
    
    def __repr__(self):
        return f"Operator({self.op})"

class SubShell:

    def __init__(self, arguments):
        self.arguments = arguments
    
    def __repr__(self):
        return f"SubShell({self.arguments})"

class Command:

    def __init__(self, cmd: list):
        self.cmd: list = cmd

    def __repr__(self):
        return f"Command({' '.join(self.cmd)})"

class Redirect:
    def __init__(self, cmd: str, file: int):
        self.cmd = cmd
        self.file = file

    def __repr__(self):
        return f"{self.__class__.__name__}(cmd={self.cmd}, file='{self.file}')"

class InputRedirect(Redirect):
    """Handles stdin redirection: command < file"""
    def __init__(self, cmd: str, file):
        super().__init__(cmd, file)

class OutputRedirect(Redirect):
    """Handles stdout redirection: command > file"""
    def __init__(self, cmd: str, file):
        super().__init__(cmd, file)

class ErrorRedirect(Redirect):
    """Handles stderr redirection: command 2> file"""
    def __init__(self, cmd: str, file):
        super().__init__(cmd, file)

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
    while cmd_cur < r and tokens[cmd_cur] not in operators:
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
            cur = l
            while cur < r and tokens[cur] != ")":
                cur+=1
            grouped_tokens.append(SubShell(token_grouper(tokens, l+1, cur)))
            l = cur+1
        elif tokens[l] in redirects:
            cmd = grouped_tokens.pop()
            l+=1
            token_sequence, l = get_token_sequence(tokens, l, r)
            grouped_tokens.append(Redirect(cmd, token_sequence[0]))
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
    LogicalOR: 10,
    LogicalAND: 20,
    Pipe: 30
}


def parser(grouped_tokens, l, r):

    precedence = None
    index = None
    op = None

    for i in range(l, r):
        token = grouped_tokens[i]
        if not isinstance(token, Operator):
            continue

        if not precedence or precedence > operator_precedence[token.op]:
            precedence = operator_precedence[token.op]
            index = i
            op = token.op

    if not precedence:
        return grouped_tokens[l]
    
    if op == "|":
        pipe = Pipe()

        pipe.add_cmd(grouped_tokens[index-1])

        while index < r and isinstance(grouped_tokens[index], Operator) and grouped_tokens[index].op == "|":
            pipe.add_cmd(grouped_tokens[index+1])
            index+=2
        
        return pipe
    
    node = op_mapping[op]()

    node.left = parser(grouped_tokens, l, index)
    node.right = parser(grouped_tokens, index+1, r)

    return node

    
    