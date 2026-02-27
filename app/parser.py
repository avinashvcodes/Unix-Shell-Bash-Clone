operators = {"|", "&&", "||", ">", ">>", "1>", "1>>"}
redirects = {">", ">>", "1>", "1>>"}

class Operator:

    def __init__(self, op):
        self.op = op
    
    def __repr__(self):
        return f"Operator({self.op})"

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

    def __init__(self, left, right):
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

def token_grouper(tokens):
    l, r = 0, len(tokens)

    grouped_tokens = []

    while l < r:
        if tokens[l] in redirects:
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
            
print(token_grouper(["ls", ">", "out.txt"]))