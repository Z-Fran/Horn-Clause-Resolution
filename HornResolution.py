from copy import deepcopy

#目标句子字典
query_dict={}
#前提句子字典
sentence_dict={}
#对谓词进行处理的前提句子字典
predicate_dict={}
#把predicate_dict的key和value互换的字典
anti_predicate_dict={}
#谓词计数
predicate_num=0
#前提子句集
KB_sentence=[]
#加入目标子句集的子句集
KB=[]
#记录归结步骤
step=[]
tree=[]

#运算符优先级表其中#为栈底符号
precedence=[
#     &  |  ~  => (  )  #
    [ 1, 1,-1, 1,-1, 1, 1],#&
    [-1, 1,-1, 1,-1, 1, 1],#|
    [ 1, 1, 1, 1,-1, 1, 1],#~
    [-1,-1,-1, 1,-1, 1, 1],#=>
    [-1,-1,-1,-1,-1, 0, 1],#(
    [ 1, 1, 1, 1, 0, 1, 1],#)
    [-1,-1,-1,-1,-1,-1, 0] ##
    ]

#运算符编号，对于运算符优先级表
def op(c):
    if c=='&':
        return 0
    elif c=='|':
        return 1
    elif c=='~':
        return 2
    elif c=='>':
        return 3
    elif c=='(':
        return 4
    elif c==')':
        return 5
    elif c=='#':
        return 6

#读取文件内容
def readFile():
    input=open("ok3.txt","r")
    query_num=int(input.readline())
    for i in range(query_num):
        query=input.readline()
        query=query.rstrip('\n')
        query=query.replace(' ','')
        if query not in query_dict:
            query_dict[i]=query
    sentence_num=int(input.readline())
    for i in range(sentence_num):
        sentence=input.readline()
        sentence=sentence.rstrip('\n')
        sentence=sentence.replace(' ','')
        if sentence not in sentence_dict:
            sentence_dict[i]=sentence

#对句子预处理：将谓词变为V+数字，将=>变为>
def preprocessInput(curstr):
    global predicate_num
    newstr=deepcopy(curstr)
    flag=True
    for i in range(len(curstr)):
        if curstr[i]>='A'and curstr[i]<='Z'and flag:
            start_pos=i
            flag=False
        elif curstr[i]==')' and curstr[i-1]!=')':
            predicate=curstr[start_pos:i+1]
            if predicate not in predicate_dict:
                predicate_dict[predicate]="V"+str(predicate_num)
                anti_predicate_dict[predicate_dict[predicate]]=predicate
                predicate_num+=1
            newstr=newstr.replace(predicate,predicate_dict[predicate])
            flag=True
    newstr.replace("=>",">") 
    return newstr

def isOperator(op):
    return op == '&' or op == '|' or op == '~' or op == '>' or op == '(' or op == ')'

#根据运算符优先级，按运算顺序将句子变成树形结构
def standardizeSentence(curstr):
    nowstr=[]
    pos=0
    while pos < len(curstr):
        if isOperator(curstr[pos]):
            nowstr.append(curstr[pos])
            pos+=1
        else:
            startpos=pos
            while pos<len(curstr) and not isOperator(curstr[pos]):
                pos+=1
            tmp=[curstr[startpos:pos]]
            nowstr.append(tmp)
    
    optr=[]
    opnd=[]
    pos=0
    optr.append('#')
    while pos<len(nowstr):
        if isinstance(nowstr[pos],list):
            opnd.append(nowstr[pos])
            pos+=1
        else:
            pop=optr.pop()
            if precedence[op(pop)][op(nowstr[pos])]<0:
                optr.append(pop)
                optr.append(nowstr[pos])
                pos+=1
            elif precedence[op(pop)][op(nowstr[pos])]>0:
                if pop=='~':
                    opnd1=opnd.pop()
                    temp=[pop,opnd1]
                    opnd.append(temp)
                else:
                    opnd2=opnd.pop()
                    opnd1=opnd.pop()
                    temp=[pop,opnd1,opnd2]
                    opnd.append(temp)
            else:
                pos+=1
    while len(optr)>1:
        pop=optr.pop()
        if pop=='~':
            opnd1=opnd.pop()
            temp=[pop,opnd1]
            opnd.append(temp)
        else:
            opnd2=opnd.pop()
            opnd1=opnd.pop()
            temp=[pop,opnd1,opnd2]
            opnd.append(temp)
    return opnd[0]

#用摩根律，给句子加否定
def negation(t):
    if len(t)==1:
        t=['~',t]
    else:
        if len(t)==2:
            t=t[1]
        else:
            if t[0]=='&':
                t[0]='|'
            else:
                t[0]='&'
            t[1]=negation(t[1])
            t[2]=negation(t[2])
    return t

#用蕴含等值式消蕴含符号
def removeImplication(t):
    if len(t)<=1:
        return t
    optr=t[0]
    if optr=='~':
           t[1]=removeImplication(t[1])
    else:
        t[1]=removeImplication(t[1])
        t[2]=removeImplication(t[2])
    if optr=='>':
        t[0]='|'
        t[1]=negation(t[1])
    return t

#否定内移
def moveNegation(t):
    if len(t)<=1:
        return t
    optr=t[0]
    if optr=='~':
        t[1]=moveNegation(t[1])
    else:
        t[1]=moveNegation(t[1])
        t[2]=moveNegation(t[2])
    if optr=='~' and len(t[1])>1:
        t=negation(t[1])
    return t

#用分配律将句子变为合取范式
def distributeAndOr(t):
    if len(t)<=1:
        return t
    optr=t[0]
    if optr=='~':
        t[1]=distributeAndOr(t[1])
    else:
        t[1]=distributeAndOr(t[1])
        t[2]=distributeAndOr(t[2])
    if op=='|':
        opnd1=t[1]
        opnd2=t[2]
        if opnd1[0]=='&':
            t1=['|',opnd1[1],opnd2]
            t2=['|',opnd1[2],opnd2]
            t=['&',t1,t2]
        elif opnd2[0]=='&':
            t1=['|',opnd1,opnd2[1]]
            t2=['|',opnd1,opnd2[2]]
            t['&',t1,t2]
    return t

def CNF(t):
    t=removeImplication(t)
    t=moveNegation(t)
    t=distributeAndOr(t)
    return t

#将句子的树状结构变为线形结构
def flatten(curlist):
    s =""
    if len(curlist) <= 1:
        return str(curlist[0])
    else:
        if len(curlist) == 3:
            s += str(flatten(curlist[1])+str(curlist[0])+flatten(curlist[2]))
        elif len(curlist) == 2:
            s+= str(str(curlist[0])+flatten(curlist[1]))
    return s

#将析取范式拆成子句
def initKBSentence(curstr):
    start_pos=0
    for i in range(len(curstr)):
        if curstr[i]=='&':
            KB_sentence.append(curstr[start_pos:i])
            start_pos=i+1
    KB_sentence.append(curstr[start_pos:len(curstr)])

#将谓词由V+数字还原为单词
def initKB():
    for curstr in KB_sentence:
        i=0
        newstr=""      
        while i<len(curstr):
            if isOperator(curstr[i]):
                newstr+=curstr[i]
                i+=1
            else:
                predicate=""
                while i<len(curstr) and not isOperator(curstr[i]):
                    predicate+=curstr[i]
                    i+=1
                newstr+=anti_predicate_dict[predicate]
        KB.append(newstr)
        
#将KnowledgeBase标准化：每一个子句都是一个字典，字典的索引是谓词，值是谓词的常量或变元列表
#比如将~Equal(A,B)变为{Equal:[[False,True,1['A','B']]]}
#第一个bool变量为谓词前的否定，第二的bool变量表示谓词中全是常量，第三个数字是常量或变元列表的唯一标识，第四个列表存放常量或变元
def standardizeKB(KB):
    count=1
    newKB=[]
    for curstr in KB:
        predicate=""
        variable=""
        ispredicate=True
        flag=True
        #enresolute=True
        tmp_dict={}
        tmp_list=[]
        variable_list=[]
        start_pos=0
        for pos in range(len(curstr)):
            if curstr[pos]=='~':
                flag=False
            elif curstr[pos]>='A' and curstr[pos]<='Z' and ispredicate:
                start_pos=pos
                ispredicate=False
            elif curstr[pos]=='(':
                predicate=curstr[start_pos:pos]
                if predicate not in tmp_dict:
                    tmp_dict[predicate]=[]
                tmp_list=[]
                tmp_list.append(flag)
                flag=True
                ispredicate=False
                variable_list=[]
                #enresolute=False
                start_pos=pos+1
            elif curstr[pos]==',':
                variable=curstr[start_pos:pos]
                # if variable[0]>='A' and variable[0]<='Z':
                #     enresolute=True
                variable_list.append(variable)
                start_pos=pos+1
            elif curstr[pos]==')':
                variable=curstr[start_pos:pos]
                # if variable[0]>='A' and variable[0]<='Z':
                #     enresolute=True
                variable_list.append(variable)
                tmp_list.append(True)
                tmp_list.append(count)
                count+=1
                tmp_list.append(variable_list)
                tmp_dict[predicate].append(tmp_list)
                ispredicate=True
        newKB.append(tmp_dict)
    return newKB
            
#将目标子句加入KnowledgeBase          
def joinKB(KB,curstr):
    count=-1
    predicate=""
    variable=""
    ispredicate=True
    flag=True
    #enresolute=False
    tmp_dict={}
    tmp_list=[]
    variable_list=[]
    start_pos=0
    for pos in range(len(curstr)):
        if curstr[pos]=='~':
             flag=False
        elif curstr[pos]>='A' and curstr[pos]<='Z' and ispredicate:
            start_pos=pos
            ispredicate=False
        elif curstr[pos]=='(':
            predicate=curstr[start_pos:pos]
            if predicate not in tmp_dict:
                tmp_dict[predicate]=[]
            tmp_list=[]
            tmp_list.append(not flag)
            flag=True
            ispredicate=False
            #enresolute=False
            start_pos=pos+1
        elif curstr[pos]==',':
            variable=curstr[start_pos:pos]
            # if variable[0]>='A' and variable[0]<='Z':
            #         enresolute=True
            variable_list.append(variable)
            start_pos=pos+1
        elif curstr[pos]==')':
            variable=curstr[start_pos:pos]
            # if variable[0]>='A' and variable[0]<='Z':
            #         enresolute=True
            variable_list.append(variable)
            tmp_list.append(True)
            tmp_list.append(count)
            count-=1
            tmp_list.append(variable_list)         
            tmp_dict[predicate].append(tmp_list)
            ispredicate=True
    KB.append(tmp_dict)
    return KB    

#开始归结
def _Resolution(Horn,Dict):
    
    # eqdict={}
    # for a in Horn:
    #     for b in a:
    #         if b == 'E':
    #             for c in a[b]:
    #                 if c[0]==True and c[3][0][0]>='A' and c[3][0][0]<='Z' and c[3][1][0]>='A' and c[3][1][0]<='Z':
    #                     eqdict[c[3][0][0]]=c[3][1][0]
    # for a in range(len(Horn)):
    #     for b in Horn[a]:
    #         for c in range(len(Horn[a][b])):
    #             for d in range(len(Horn[a][b][c][3])):
    #                 if Horn[a][b][c][3][d] in eqdict:
    #                     Horn[a][b][c][3][d]=eqdict[Horn[a][b][c][3][d]]
                        
                    
                        
    
    curlist=[Horn.index(Dict),list(Dict.keys())[0],0]
                
    pos_i=0
    pos_predicate=""
    pos_j=0
    exlist=[]
    
    for i in range(len(Horn)):
        if i==curlist[0]:
            continue
        for predicate in Horn[i]:
             #寻找谓词相同的子句
            if predicate==curlist[1]:
                for j in range(len(Horn[i][predicate])):
                    find=False
                    #寻找互反谓词
                    if Horn[i][predicate][j][0]!=Horn[curlist[0]][curlist[1]][curlist[2]][0]:
                        #判断谓词是否可替换
                        find=True
                        for k in range(len(Horn[i][predicate][j][3])):
                            if Horn[i][predicate][j][3][k][0]>='A' and Horn[i][predicate][j][3][k][0]<='Z' and Horn[curlist[0]][curlist[1]][curlist[2]][3][k][0]>='A' and Horn[curlist[0]][curlist[1]][curlist[2]][3][k][0]<='Z' and Horn[i][predicate][j][3][k]!=Horn[curlist[0]][curlist[1]][curlist[2]][3][k]:
                                find=False
                            if Horn[i][predicate][j][3][k][0]=="@" and Horn[curlist[0]][curlist[1]][curlist[2]][3][k][0]>='A' and Horn[curlist[0]][curlist[1]][curlist[2]][3][k][0]<='Z':
                                find=False
                            if Horn[curlist[0]][curlist[1]][curlist[2]][3][k][0]=="@" and Horn[i][predicate][j][3][k][0]>='A' and Horn[i][predicate][j][3][k][0]<='Z':
                                find=False
                    if find:
                        displace=[]
                        pos_i=i
                        pos_predicate=predicate
                        pos_j=j
                        exlist=deepcopy(curlist)
                        newHorn=deepcopy(Horn)
                        temp1=[newHorn[curlist[0]]]
                        temp2=[newHorn[pos_i]]
                        tree.append([disstandardize(temp1)[0],disstandardize(temp2)[0]])
                        step.append(newHorn)
                        #newHorn.append(Horn[pos_i])
                        #newHorn.append(newHorn[exlist[0]])
                        ex={}
                        #构造变元替换表
                        for k in range(len(newHorn[pos_i][pos_predicate][pos_j][3])):
                            if (newHorn[pos_i][pos_predicate][pos_j][3][k][0]>='a' and newHorn[pos_i][pos_predicate][pos_j][3][k][0]<='z') and newHorn[exlist[0]][exlist[1]][exlist[2]][3][k][0]!='@' and newHorn[pos_i][pos_predicate][pos_j][3][k]!=newHorn[exlist[0]][exlist[1]][exlist[2]][3][k]:
                                ex[newHorn[pos_i][pos_predicate][pos_j][3][k]]=newHorn[exlist[0]][exlist[1]][exlist[2]][3][k]
                                displace.append(newHorn[exlist[0]][exlist[1]][exlist[2]][3][k]+"/"+newHorn[pos_i][pos_predicate][pos_j][3][k])
                               
                        for k in range(len(newHorn[pos_i][pos_predicate][pos_j][3])):
                            if newHorn[pos_i][pos_predicate][pos_j][3][k][0]=='@' and (newHorn[exlist[0]][exlist[1]][exlist[2]][3][k][0]>='a' and newHorn[exlist[0]][exlist[1]][exlist[2]][3][k][0]<='z') and newHorn[pos_i][pos_predicate][pos_j][3][k][2:] in ex and ex[newHorn[pos_i][pos_predicate][pos_j][3][k][2]]>='A' and ex[newHorn[pos_i][pos_predicate][pos_j][3][k][2]]<='Z':
                                ex[newHorn[pos_i][pos_predicate][pos_j][3][k]]=newHorn[pos_i][pos_predicate][pos_j][3][k][1].upper()+ex[newHorn[pos_i][pos_predicate][pos_j][3][k][2:]]
                        #构造根据变元替换表对子句进行更新
                        for p in newHorn[pos_i]:
                            for k in range(len(newHorn[pos_i][p])):
                                for l in range(len(newHorn[pos_i][p][k][3])):
                                    if newHorn[pos_i][p][k][3][l] in ex:
                                        newHorn[pos_i][p][k][3][l]=ex[newHorn[pos_i][p][k][3][l]]
        
                        ex={}
                        #构造变元替换表
                        for k in range(len(newHorn[exlist[0]][exlist[1]][exlist[2]][3])):
                            if (newHorn[exlist[0]][exlist[1]][exlist[2]][3][k][0]>='a' and newHorn[exlist[0]][exlist[1]][exlist[2]][3][k][0]<='z') and (newHorn[pos_i][pos_predicate][pos_j][3][k][0]>='A' and newHorn[pos_i][pos_predicate][pos_j][3][k][0]<='Z'):
                                ex[newHorn[exlist[0]][exlist[1]][exlist[2]][3][k]]=newHorn[pos_i][pos_predicate][pos_j][3][k]
                                displace.append(newHorn[pos_i][pos_predicate][pos_j][3][k]+"/"+newHorn[exlist[0]][exlist[1]][exlist[2]][3][k])
                        for k in range(len(newHorn[exlist[0]][exlist[1]][exlist[2]][3])):
                            if newHorn[exlist[0]][exlist[1]][exlist[2]][3][k][0]=='@' and (newHorn[pos_i][pos_predicate][pos_j][3][k][0]>='a' and newHorn[pos_i][pos_predicate][pos_j][3][k][0]<='z') and newHorn[exlist[0]][exlist[1]][exlist[2]][3][k][2:] in ex and ex[newHorn[exlist[0]][exlist[1]][exlist[2]][3][k][2]]>='A' and ex[newHorn[exlist[0]][exlist[1]][exlist[2]][3][k][2]]<='Z':
                                ex[newHorn[exlist[0]][exlist[1]][exlist[2]][3][k]]=newHorn[exlist[0]][exlist[1]][exlist[2]][3][k][1].upper()+ex[newHorn[exlist[0]][exlist[1]][exlist[2]][3][k][2:]]
                        #构造根据变元替换表对子句进行更新
                        for p in newHorn[exlist[0]]:
                            for k in range(len(newHorn[exlist[0]][p])):
                                for l in range(len(newHorn[exlist[0]][p][k][3])):
                                    if newHorn[exlist[0]][p][k][3][l] in ex:
                                        newHorn[exlist[0]][p][k][3][l]=ex[newHorn[exlist[0]][p][k][3][l]]
                        
                        ex={}
                        #构造变元替换表
                        for k in range(len(newHorn[pos_i][pos_predicate][pos_j][3])):
                            if (newHorn[pos_i][pos_predicate][pos_j][3][k][0]>='a' and newHorn[pos_i][pos_predicate][pos_j][3][k][0]<='z') and (newHorn[exlist[0]][exlist[1]][exlist[2]][3][k][0]>='A' and newHorn[exlist[0]][exlist[1]][exlist[2]][3][k][0]<='Z'):
                                ex[newHorn[pos_i][pos_predicate][pos_j][3][k]]=newHorn[exlist[0]][exlist[1]][exlist[2]][3][k]
                                displace.append(newHorn[exlist[0]][exlist[1]][exlist[2]][3][k]+newHorn[pos_i][pos_predicate][pos_j][3][k])
                        for k in range(len(newHorn[pos_i][pos_predicate][pos_j][3])):
                            if newHorn[pos_i][pos_predicate][pos_j][3][k][0]=='@'  and (newHorn[pos_i][pos_predicate][pos_j][3][k][0]>='a' and newHorn[pos_i][pos_predicate][pos_j][3][k][0]<='z') and newHorn[pos_i][pos_predicate][pos_j][3][k][2:] in ex and ex[newHorn[pos_i][pos_predicate][pos_j][3][k][2]]>='A' and ex[newHorn[pos_i][pos_predicate][pos_j][3][k][2]]<='Z':
                                ex[newHorn[pos_i][pos_predicate][pos_j][3][k]]=newHorn[pos_i][pos_predicate][pos_j][3][k][1].upper()+ex[newHorn[pos_i][pos_predicate][pos_j][3][k][2:]]
                        #构造根据变元替换表对子句进行更新
                        for p in newHorn[pos_i]:
                            for k in range(len(newHorn[pos_i][p])):
                                for l in range(len(newHorn[pos_i][p][k][3])):
                                    if newHorn[pos_i][p][k][3][l] in ex:
                                        newHorn[pos_i][p][k][3][l]=ex[newHorn[pos_i][p][k][3][l]]
                        ex={}
                        for k in range(len(newHorn[pos_i][pos_predicate][pos_j][3])):
                            if (newHorn[pos_i][pos_predicate][pos_j][3][k][0]>='a' and newHorn[pos_i][pos_predicate][pos_j][3][k][0]<='z') and newHorn[exlist[0]][exlist[1]][exlist[2]][3][k][0]=='@':
                                ex[newHorn[pos_i][pos_predicate][pos_j][3][k]]=newHorn[exlist[0]][exlist[1]][exlist[2]][3][k]
                                displace.append(newHorn[exlist[0]][exlist[1]][exlist[2]][3][k]+"/"+newHorn[pos_i][pos_predicate][pos_j][3][k])
                        #构造根据变元替换表对子句进行更新
                        for p in newHorn[pos_i]:
                            for k in range(len(newHorn[pos_i][p])):
                                for l in range(len(newHorn[pos_i][p][k][3])):
                                    if newHorn[pos_i][p][k][3][l] in ex:
                                        newHorn[pos_i][p][k][3][l]=ex[newHorn[pos_i][p][k][3][l]]
                        ex={}
                        for k in range(len(newHorn[exlist[0]][exlist[1]][exlist[2]][3])):
                            if (newHorn[exlist[0]][exlist[1]][exlist[2]][3][k][0]>='a' and newHorn[exlist[0]][exlist[1]][exlist[2]][3][k][0]<='z') and newHorn[pos_i][pos_predicate][pos_j][3][k][0]=='@':
                                ex[newHorn[exlist[0]][exlist[1]][exlist[2]][3][k]]=newHorn[pos_i][pos_predicate][pos_j][3][k]
                                displace.append(newHorn[pos_i][pos_predicate][pos_j][3][k]+"/"+newHorn[exlist[0]][exlist[1]][exlist[2]][3][k])
                        #构造根据变元替换表对子句进行更新
                        for p in newHorn[exlist[0]]:
                            for k in range(len(newHorn[exlist[0]][p])):
                                for l in range(len(newHorn[exlist[0]][p][k][3])):
                                    if newHorn[exlist[0]][p][k][3][l] in ex:
                                        newHorn[exlist[0]][p][k][3][l]=ex[newHorn[exlist[0]][p][k][3][l]] 
                        
                        tree[-1].append(displace)
                        Horn1_exist=True
                        Horn2_exist=True
                        tmpdict={}
                        ex_dict1=newHorn[pos_i]
                        ex_dict2=newHorn[exlist[0]]
                        
                        F=True
                        for p in ex_dict1:
                            for k in ex_dict1[p]:
                                for l in k[3]:
                                    if l[0]<'A' or l[0]>'Z':
                                        F=False
                                        break
                        if F:
                            newHorn.append(ex_dict1)
                            
                        F=True
                        for p in ex_dict2:
                            for k in ex_dict2[p]:
                                for l in k[3]:
                                    if l[0]<'A' or l[0]>'Z':
                                        F=False
                                        break
                        if F:
                            newHorn.append(ex_dict2)
                        
                        #删除匹配子句的规约部分
                        if len(newHorn[pos_i])==1 and len(newHorn[pos_i][pos_predicate])==1:
                            newHorn.remove(newHorn[pos_i])
                            Horn1_exist=False
                        elif len(newHorn[pos_i])!=1 and len(newHorn[pos_i][pos_predicate])==1:
                            newHorn[pos_i].pop(pos_predicate)
                        else:
                            newHorn[pos_i][pos_predicate].remove(newHorn[pos_i][pos_predicate][pos_j])

                        for x in range(len(newHorn)):
                            if newHorn[x]==ex_dict2:
                                exlist[0]=x
  
                        if len(newHorn[exlist[0]])==1 and len(newHorn[exlist[0]][exlist[1]])==1:
                            newHorn.remove(newHorn[exlist[0]])
                            Horn2_exist=False
                        elif len(newHorn[exlist[0]])!=1 and len(newHorn[exlist[0]][exlist[1]])==1:
                            newHorn[exlist[0]].pop(exlist[1])
                        else:
                            newHorn[exlist[0]][exlist[1]].remove(newHorn[exlist[0]][exlist[1]][exlist[2]])
                        
                        
                        for x in range(len(newHorn)):
                            if newHorn[x]==ex_dict1:
                                pos_i=x
                        for x in range(len(newHorn)):
                            if newHorn[x]==ex_dict2:
                                exlist[0]=x
                        
                        if  not Horn1_exist and not Horn2_exist:
                            return True                
                        #合并匹配子句的剩余部分
                        elif Horn1_exist and Horn2_exist:                
                            for p in newHorn[pos_i]:
                                if p not in tmpdict:
                                    tmpdict[p]=newHorn[pos_i][p]
                                else:
                                    tmpdict[p]+=newHorn[pos_i][p]
                            for p in newHorn[exlist[0]]:
                                if p not in tmpdict:
                                    tmpdict[p]=newHorn[exlist[0]][p]
                                else:
                                    tmpdict[p]+=newHorn[exlist[0]][p]
                            newHorn.remove(newHorn[pos_i])
                            for x in range(len(newHorn)):
                                if newHorn[x]==ex_dict2:
                                    exlist[0]=x
                            newHorn.remove(newHorn[exlist[0]])
                            newHorn.append(tmpdict)
                        
                        elif Horn1_exist and not Horn2_exist:
                            tmpdict=newHorn[pos_i]
                        elif not Horn1_exist and Horn2_exist:
                            tmpdict=newHorn[exlist[0]]
                        # if Horn[i] not in newHorn:
                        #     print(1)
                        #     newHorn.append(Horn[i])
                        #递归地进行下一次规约
                        
                        # print(disstandardize(newHorn))
                        # print("____________") 
                        result=_Resolution(newHorn,tmpdict)
                        if result:
                            return True
                        else:
                            step.pop()
                            tree.pop()
                     
    return False                 

def Resolution(Horn):
    for Dict in Horn:
        result=_Resolution(Horn,Dict)
        if result:
            return True
    return False

def disstandardize(curlist):
    showHorn=[]
    for curdict in curlist:
        curstr=""
        for p in curdict:
            for q in curdict[p]:
                if not q[0]:
                   curstr+='~'
                curstr+=p
                curstr+='('
                for ch in q[3]:
                    curstr+=ch
                    curstr+=','
                curstr=curstr[0:-1]
                curstr+=')'
                curstr+='|'
        curstr=curstr[0:-1]
        curstr+=''
        showHorn.append(curstr)
    return showHorn

def Run(clause,result):
    global query_dict
    global sentence_dict
    global predicate_dict
    global anti_predicate_dict
    global predicate_num
    global KB_sentence
    global KB
    global step
    global tree

    query_dict = {}
    sentence_dict = {}
    predicate_dict = {}
    anti_predicate_dict = {}
    predicate_num = 0
    KB_sentence = []
    KB = []
    step = []
    tree = []

    query_dict[0]=result
    clause=clause.split('\n')
    i = 0
    for c in clause:
        sentence_dict[i]= c
        i+=1
    print(query_dict)
    print(sentence_dict)
    for i in sentence_dict:
        initKBSentence(flatten(CNF(standardizeSentence(preprocessInput(sentence_dict[i])))))
    initKB()
    KB = standardizeKB(KB)
    tmpKB = deepcopy(KB)
    tmpKB = joinKB(tmpKB, query_dict[0])
    flag = bool()
    print("##########################################")
    step.append(tmpKB)
    flag = Resolution(tmpKB)
    if flag:
        print("TRUE")
        return True, tree
    else:
        print("FALSE")
        return False, None

if __name__=="__main__":
    readFile()
    for i in sentence_dict:
        initKBSentence(flatten(CNF(standardizeSentence(preprocessInput(sentence_dict[i])))))
    #print(KB_sentence)
    initKB()
    #print(KB)
    KB=standardizeKB(KB)
    #print(KB)

    for i in query_dict:
        tmpKB=deepcopy(KB)
        tmpKB=joinKB(tmpKB,query_dict[i])
        flag=bool()
        # for curdict in tmpKB:
        #     print(curdict)
        print("##########################################")
        step.append(tmpKB)
        flag=Resolution(tmpKB)
        if flag:
            print("TRUE")
            for s in step:
                show=disstandardize(s)
                print("------------------------------------------")
                for s in show:
                    print(s)
                print("------------------------------------------")
            for s in tree:
                print("==========================================")
                print(s)
                print("==========================================")
        else:
            print("FALSE")
        print("##########################################")
        step=[]