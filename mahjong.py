from json import load
from hashlib import sha256
from datetime import datetime
import random


with open("./data/name.json",'r',encoding='utf-8') as f:
    mname=load(f)

class Mahjong:
    def __init__(self, code:int):
        self.code=code
        self.cate=self.code//4
        self.name:list=mname[str(self.cate)]
        if self.cate not in [8,17,26,30,33]:
            self.dora:list=mname[str(self.cate+1)]
        elif self.cate in [8,17,26]:
            self.dora:list=mname[str(self.cate-8)]
        else:
            self.dora:list=mname[27 if self.cate==30 else 31]
    
    def __str__(self):
        return self.name[0]
            
def generate_mountain(gsd:int)->list:
    """
    生成山牌
    """
    seed=sha256((str(gsd)+datetime.now().strftime("%Y-%m-%d %H:%M:%S")).encode()).hexdigest()
    random.seed(seed)
    mountain=[Mahjong(i) for i in range(136)]
    random.shuffle(mountain)
    return mountain

def get_money(fan:int,fu:int,zhuang:bool,tsumo:bool,honn:int)->list:
    pass

def unique_results(results):
    seen = []
    for r in results:
        norm = set(tuple(sorted(t)) for t in r)
        if not any(set(tuple(sorted(t)) for t in s) == norm for s in seen):
            seen.append(r)
    return seen


def is_ron(datainfo:dict)->dict: 
    '''
    datainfo:{
        "hand":[Mahjong,...],
        "final":Mahjong,
        "furu":[(0,Mahjong,...),...], : 0-pon; 1-chi; 2-ankan; 3-minkan; 4-pokan.
        "riichi":bool,
        "ippatu":bool,
        "daburu":bool,
        "changfeng":int, : 0123
        "zifeng":int,
        "tumo":bool,
        "furuiyaku":bool,
        "self":bool, #庄家or not
        "qianggang":bool,
        "ganghua":bool,
        "river":bool,
        "sea":bool,
        "dora":list,
        "ridora":list,
        $"yanfan":bool,
        $"gangzhen":bool
    }
    '''
    result={"ron":False,"fan":0,"fu":0,"money":0}
    pai:list=datainfo["hand"]
    final:Mahjong=datainfo["final"]
    furu:list=datainfo["furu"]
    _fr=[]
    for i in furu:
        if len(i)==4:
            _fr.append((i[0],i[1].cate,i[2].cate,i[3].cate))
        else:
            _fr.append((i[0],i[1].cate,i[2].cate,i[3].cate,i[4].cate))
    furu=_fr.copy()
    under_info={
        "x":[],
        "riichi":datainfo["riichi"],
        "ippatu":datainfo["ippatu"],
        "daburu":datainfo["daburu"],
        "changfeng":datainfo["changfeng"],
        "zifeng":datainfo["zifeng"],
        "furuiyaku":datainfo["furuiyaku"],
        "tumo":datainfo["tumo"]
    }
    x=[]
    
    pai.append(final)
    testpi=[i.cate for i in pai]
    ques=[i for i in testpi if testpi.count(i)>=2]
    for quetou in ques:
        this_pi=[i for i in testpi]
        this_pi.remove(quetou)
        this_pi.remove(quetou)
        possibleke=list(set([i for i in this_pi if this_pi.count(i)>=3]))
        
        #$ 步骤1：去掉全部顺子
        s1=[i for i in this_pi]
        menzi=len(furu)
        po=[(quetou,quetou)]
        for i in s1:
            if i % 9 < 7 and i < 27:
                while i in s1 and i+1 in s1 and i+2 in s1:
                    s1.remove(i)
                    s1.remove(i+1)
                    s1.remove(i+2)
                    po.append((i,i+1,i+2,))
                    menzi+=1
                    
        if menzi == 4 or (all(s1.count(x) == 3 for x in s1)):
            for ssss in list(set(s1)):
                po.append((ssss,ssss,ssss))
            x.append(po)
        
        #$ 步骤2：遍历去掉一个刻子
        for singlekezi in possibleke:
            s2=this_pi.copy()
            menzi=len(furu)+1
            s2.remove(singlekezi)
            s2.remove(singlekezi)
            s2.remove(singlekezi)
            po=[(quetou,quetou),(singlekezi,singlekezi,singlekezi)]
            for i in s2:
                if i % 9 < 7 and i < 27:
                    while i in s2 and i+1 in s2 and i+2 in s2:
                        s2.remove(i)
                        s2.remove(i+1)
                        s2.remove(i+2)
                        po.append((i,i+1,i+2,))
                        menzi+=1
            if menzi == 4 or (menzi + len(possibleke) == 4 and all(s2.count(x) == 3 for x in s2)):
                for ssss in s2:
                    if ssss != singlekezi:
                        po.append((ssss,ssss,ssss))
                x.append(po)
        
        #$ 步骤3：去掉所有刻子
        s3=[i for i in this_pi if i not in possibleke]
        menzi=len(furu)+len(possibleke)
        po=[(quetou,quetou)]
        for i in s3:
            if i % 9 < 7 and i < 27:
                while i in s3 and i+1 in s3 and i+2 in s3:
                    s3.remove(i)
                    s3.remove(i+1)
                    s3.remove(i+2)
                    po.append((i,i+1,i+2))
                    menzi+=1
        if menzi == 4:
            for ssss in possibleke:
                po.append((ssss,ssss,ssss))
            x.append(po)
        
    if len(x)>0:
        result["ron"]=True
        x=unique_results(x)
        for i in x:
            i.extend(furu)
        if __name__ == "__main__":
            for i in x:
                print(i)
    else:
        return result


def is_tenpai(pai:dict)->list:
    pass

if __name__ == "__main__":
    ttst={
        "hand":[Mahjong(4),Mahjong(5),Mahjong(6),Mahjong(8),Mahjong(9),Mahjong(10),Mahjong(12),Mahjong(13),Mahjong(14),Mahjong(108)],
        "final":Mahjong(109),
        "furu":[(0,Mahjong(0),Mahjong(1),Mahjong(2))],
        "riichi":False,
        "ippatu":False,
        "daburu":False,
        "changfeng":0,
        "zifeng":0,
        "furuiyaku":False,
        "tumo":True,
        "self":True,
        "qianggang":False,
        "ganghua":False,
        "river":False,
        "sea":False
    }
    is_ron(ttst)