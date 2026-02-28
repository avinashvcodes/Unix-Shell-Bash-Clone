def tokenize(s: str):

    l, r = 0, len(s)
    tokens = []
    while l<r:

        while l<r and s[l].isspace():
            l+=1

        if l==r:
            break

        in_single_quote = False
        in_double_quote = False

        word = ""
        while l<r:
            if not in_single_quote and not in_double_quote:
                if s[l].isspace():
                    l+=1
                    break
                if s[l] == "(" or s[l] == ")":
                    if word:
                        tokens.append(word)
                        word = ""
                    tokens.append(s[l])
                    l+=1
                    break
                if s[l] == "&":
                    if word:
                        tokens.append(word)
                        word = ""
                    if l+1 < r and s[l+1] == "&":
                        word+="&&"
                        l+=2
                    else:
                        word+="&"
                        l+=1
                    break
                if s[l] == "|":
                    if word:
                        tokens.append(word)
                        word = ""
                    if l+1 < r and s[l+1] == "|":
                        word+="||"
                        l+=2
                    else:
                        word+="|"
                        l+=1
                    break
                if s[l] == ">":
                    if word and word not in ("1", "2"):
                        tokens.append(word)
                        word = ""
                    if s[l+1] == ">":
                        word+=">>"
                        l+=2
                    else:
                        word+=">"
                        l+=1
                    break
                if s[l] == "\\" and l+1 < r:
                    word+=s[l+1]
                    l+=2
                    continue

            if in_double_quote and s[l] == "\\" and l+1 < r and s[l+1] in ("\"", "\\", "$", "`"):
                word+=s[l+1]
                l+=2
                continue


            if s[l] == "'" and not in_double_quote:
                in_single_quote = not in_single_quote

            elif s[l] == '"' and not in_single_quote:
                in_double_quote = not in_double_quote

            else:
                word+=s[l]

            l+=1

        if word:
            tokens.append(word)

    return tokens
