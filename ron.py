oppai=[(27,27),(0,0,0),(8,8,8),(9,9,9),(1,16,17,18)]
def isyaojiu(pai:int)->bool:
    if isinstance(pai, int):
        return pai%9 in [0,8] or pai>=27
    return False    

if all((len(ppp)==3 and (isyaojiu(ppp[0]) or isyaojiu(ppp[2]))) or (len(ppp)!=3 and (isyaojiu(ppp[1]) or (len(ppp)==4 and ppp[0]==1 and isyaojiu(ppp[3])))) for ppp in oppai):
    print(True)