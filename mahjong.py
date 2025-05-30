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
        self.truecate=self.cate if self.code not in [16,52,88] else self.cate//36+34
        self.name:list=mname[str(self.truecate)]
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
        "furu":[(int,Mahjong),...], : 
            0-pon; 1-chi; 2-ankan; 3-minkan; 4-pokan.
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
    
    Returns:
    dict:{
        "ron":bool,
        "fan":int,
        "fu":int(役满为0),
        "final_shape":list[tuple,Mahjong], 最终用于计算分数的和牌牌型，tuple是手牌&副露，Mahjong是所和牌
        "yaku":list[str]
    }
    
    '''
    result={"ron":False,"fan":0,"fu":0,"final_shape":[],"yaku":[]}
    pai:list=datainfo["hand"]
    final:Mahjong=datainfo["final"]
    furu:list=datainfo["furu"]
    _fr=[]
    menqing=len(furu)==0 or all(i[0]==2 for i in furu) #$门清
    for i in furu:
        if len(i)==4:
            _fr.append((i[0],i[1].cate,i[2].cate,i[3].cate))
        else:
            _fr.append((i[0],i[1].cate,i[2].cate,i[3].cate,i[4].cate))
    furu=_fr.copy()
    x=[]
    
    ###$ 国士无双
    if set([i.cate for i in (pai+[final])]) == {0,8,9,17,18,26,27,28,29,30,31,32,33}:
        result["fan"]=100
        result["fu"]=0
        result["ron"]=True
        result["final_shape"]=[tuple(pai),final]
        if set(pai)=={0,8,9,17,18,26,27,28,29,30,31,32,33}:
            result["fan"]*=2
            result["yaku"].append("国士无双十三面")
        else:
            result["yaku"].append("国士无双")
    if result["ron"]:
        return result
    
    ###$ 七对子
    if len(list(set(pai+[final])))==7 and all((pai+[final]).count(i)==2 for i in list(set(pai+[final]))):
        result["ron"]=True
        result["fan"]+=2
        result["fu"]=25
        result["yaku"].append("七对子")
        result["final_shape"]=[tuple(pai),final]
    
    ###$ 和牌型

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
        po=[(quetou,)]
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
            po=[(quetou,),(singlekezi,singlekezi,singlekezi)]
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
        po=[(quetou,)]
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
        for hupai in x:
            hupai.extend(furu)
    elif len(list(set(pai+[final])))==7 and all((pai+[final]).count(i)==2 for i in list(set(pai+[final]))): #$ 不满足二杯口的可能满足七对子。满足二杯口的(len(x)>0)一律不按七对子算
        result["ron"]=True
        result["fan"]+=2
        result["fu"]=25
        result["yaku"].append("七对子")
        result["final_shape"]=[tuple(pai),final]
        x=[tuple(pai+[final])]

    if result["ron"]:
        unzip_pai=[]
        if len(result["yaku"])!=0:
            unzip_pai=list(x[0])
        else:
            unzip_pai=[i for i in pai]
            for i in furu: 
                if len(i)==4:
                    unzip_pai.append((i[1],i[2],i[3]))
                else:
                    unzip_pai.append((i[1],i[2],i[3],i[4]))
                    
                unzip_pai=unzip_pai+[j for j in i] 
            unzip_pai.append(final) #!注意在判断某些役种时unzip_pai不再有效
        
        #$ 字一色
        if all(i.cate>26 for i in unzip_pai):
            result["fan"]+=100
            result["fu"]=0
            result["yaku"].append("字一色")
        
        #$ 四暗刻&单骑
        if menqing and all(unzip_pai.count(i)>=3 for i in unzip_pai if i.cate!=final.cate):
            if pai.count(final)==1:
                result["fan"]+=200
                result["fu"]=0
                result["yaku"].append("四暗刻单骑")
            elif pai.count(final)==2 and datainfo["tumo"]:
                result["fan"]+=100
                result["fu"]=0
                result["yaku"].append("四暗刻")
        
        #$ 九莲宝灯&纯正
        if len(furu)==0 and len(list(set([i//9 for i in unzip_pai])))==1 and "字一色" not in result["yaku"]:
            xhand=[i.cate%9 for i in unzip_pai]
            if set(xhand)=={0,1,2,3,4,5,6,7,8} and xhand.count(0)>=3 and xhand.count(8)>=3:
                result["fu"]=0
                if sorted([i.cate%9 for i in pai])==[0,0,0,1,2,3,4,5,6,7,8,8,8]:
                    result["fan"]+=200
                    result["yaku"].append("纯正九莲宝灯")
                else:
                    result["fan"]+=100
                    result["yaku"].append("九莲宝灯")
        
        #$ 大四喜
        if all(i.cate in [27,28,29,30] and unzip_pai.count(i)>=3 for i in unzip_pai if i.cate!=x[0][0][0]):
            result["fan"]+=200
            result["fu"]=0
            result["yaku"].append("大四喜")
            
        #$ 小四喜
        feng_cates = [27, 28, 29, 30]
        feng_ke = [i for i in feng_cates if unzip_pai.count(i) >= 3]
        feng_quetou = [i for i in feng_cates if unzip_pai.count(i) == 2]
        if len(feng_ke) == 3 and len(feng_quetou) == 1:
            result["fan"] += 100
            result["fu"] = 0
            result["yaku"].append("小四喜")
            
        #$ 大三元
        yuan_cates = [31, 32, 33]
        yuan_ke = [i for i in yuan_cates if unzip_pai.count(i) >= 3]
        if len(yuan_ke) == 3:
            result["fan"] += 100
            result["fu"] = 0
            result["yaku"].append("大三元")
        
        #$ 绿一色
        if all(i.cate in [19,20,21,23,25,32] for i in unzip_pai):
            result["fan"]+=100
            result["fu"]=0
            result["yaku"].append("绿一色")
            
        #$ 清老头
        if all(i.cate in [0,8,9,17,18,26] for i in unzip_pai) and len(furu)==0:
            result["fan"]+=100
            result["fu"]=0
            result["yaku"].append("清老头")
            
        #$ 四杠子
        if len(furu)==4 and all(i[0]>=2 for i in furu):
            result["fan"]+=100
            result["fu"]=0
            result["yaku"].append("四杠子")
        
        ###$ 六番
        ##$ 清一色
        if len(list(set([i.cate//9 for i in unzip_pai])))==1:
            #? 有字一色的会自动清除清一色
            result["fan"]+=(5+menqing)
            result["yaku"].append("清一色")
        
        ###$ 三番
        ##$ 二杯口
        if menqing and len(list(set(unzip_pai)))==7 and all(unzip_pai.count(i)==2 for i in list(set(unzip_pai))):
            result["fan"]+=3
            result["yaku"].append("二杯口")
            
        ##$ 混一色
        if len(list(set([i.cate//9 for i in unzip_pai])))==2 and 3 in list(set([i.cate//9 for i in unzip_pai])):
            result["fan"]+=(2+menqing)
            result["yaku"].append("混一色")
        
        ###$ 两番
        #!七对子已判断
        
        ##$ 三杠子
        
        ##$ 小三元
        
        ##$ given
        if datainfo["daburu"]:
            result["fan"]+=1
            result["yaku"].append("双立直")
        
        
        ###$ 一番
        
        ##$ 断幺九
        if all(i.cate%9 not in [0,8] and i.cate<27 for i in unzip_pai):
            result["fan"]+=1
            result["yaku"].append("断幺九")
        
        
        ##$ 门清自摸
        if menqing and datainfo["tumo"]:
            result["fan"]+=1
            result["yaku"].append("门清自摸")
            
        ##$ 役牌
        xhand=[i.cate for i in unzip_pai if i.cate >26 and unzip_pai.count(i)>=3]
        if datainfo["changfeng"] in xhand:
            result["fan"]+=1
            result["yaku"].append("役牌:场风")
        if datainfo["zifeng"] in xhand:
            result["fan"]+=1
            result["yaku"].append("役牌:自风")
        if 31 in xhand:
            result["fan"]+=1
            result["yaku"].append("役牌:白")
        if 32 in xhand:
            result["fan"]+=1
            result["yaku"].append("役牌:发")
        if 33 in xhand:
            result["fan"]+=1
            result["yaku"].append("役牌:中")


        ##$ given
        if datainfo["riichi"]:
            result["fan"]+=1
            if not datainfo["daburu"]:
                result["yaku"].append("立直")
        if datainfo["qianggang"]:
            result["fan"]+=1
            result["yaku"].append("枪杠")
        if datainfo["ganghua"]:
            result["fan"]+=1
            result["yaku"].append("岭上开花")
        if datainfo["ippatu"]:
            result["fan"]+=1
            result["yaku"].append("一发")
        if datainfo["sea"]:
            result["fan"]+=1
            result["yaku"].append("海底捞月")
        if datainfo["river"]:
            result["fan"]+=1
            result["yaku"].append("河底捞鱼")
        
        
        #$ dora
        
        #$ ridora
        
        fans={i:{"fan":result["fan"],"fu":0,"yaku":result["yaku"],"final_shape":[]} for i in range(len(x))}
        pass #! 差一个finalshape没写
            
        def isyaojiu(pai:Mahjong|int)->bool:
            if isinstance(pai, Mahjong):
                return pai.cate%9 in [0,8] or pai.cate>=27
            elif isinstance(pai, int):
                return pai%9 in [0,8] or pai>=27
            return False

        #$ 多种拆牌的
        for ssm in range(len(x)):
            oppai=x[ssm].copy()

            ##$ 纯全带幺九**->3f-1f
            if all(i<27 for i in unzip_pai) and all(i.cate%9 not in [3,4,5] for i in unzip_pai) and not any((len(ppppp)==2 and ppppp[0]%9 not in [0,8]) or (len(ppppp)==3 and not (ppppp[0]%9==0 or ppppp[2]%9==8)) or (len(ppppp)==4 and not (ppppp[1]%9==0 or ppppp[3]%9==8)) or (len(ppppp)==5 and not ppppp[1]%9 in [0,8]) for ppppp in oppai):
                fans[ssm]["fan"]+=(2+menqing)
                fans[ssm]["yaku"].append("纯全带幺九")
            ##$ 一气通贯**->2f-1f
            if any((len(ppp)==3 and ppp[0]!=ppp[1] and ppp[0]%9==0 and ((ppp[0]+3,ppp[0]+4,ppp[0]+5,) in oppai or (1,ppp[0]+3,ppp[0]+4,ppp[0]+5,) in oppai) and ((ppp[0]+6,ppp[0]+7,ppp[0]+8,) in oppai or (1,ppp[0]+6,ppp[0]+7,ppp[0]+8,) in oppai)) or (len(ppp)==4 and ppp[0]==1 and ppp[1]%9==0 and ((ppp[1]+3,ppp[1]+4,ppp[1]+5,) in oppai or (1,ppp[1]+3,ppp[1]+4,ppp[1]+5,) in oppai) and ((ppp[1]+6,ppp[1]+7,ppp[1]+8,) in oppai or (1,ppp[1]+6,ppp[1]+7,ppp[1]+8,) in oppai)) for ppp in oppai):
                fans[ssm]["fan"]+=(1+menqing)
                fans[ssm]["yaku"].append("一气通贯")
                break
            
            ##$ 混全带幺九**->2f-1f
            if "纯全带幺九" not in fans[ssm]["yaku"] and all((len(ppp)==3 and (isyaojiu(ppp[0]) or isyaojiu(ppp[2]))) or (len(ppp)!=3 and (isyaojiu(ppp[1]) or (len(ppp)==4 and ppp[0]==1 and isyaojiu(ppp[3])))) for ppp in oppai):
                fans[ssm]["fan"]+=(1+menqing)
                fans[ssm]["yaku"].append("混全带幺九")
            
            ##$ 三色同顺**->2f-1f
            if any((len(ppp)==3 and ppp[0]!=ppp[1] and ((ppp[0]+9,ppp[0]+10,ppp[0]+11,) in oppai or (1,ppp[0]+9,ppp[0]+10,ppp[0]+11,) in oppai) and ((ppp[0]+18,ppp[0]+19,ppp[0]+20,) in oppai or (1,ppp[0]+18,ppp[0]+19,ppp[0]+20,) in oppai)) or (len(ppp)==4 and ppp[0]==1 and ((ppp[1]+9,ppp[1]+10,ppp[1]+11,) in oppai or (1,ppp[1]+9,ppp[1]+10,ppp[1]+11,) in oppai) and ((ppp[1]+18,ppp[1]+19,ppp[1]+20,) in oppai or (1,ppp[1]+18,ppp[1]+19,ppp[1]+20,) in oppai)) for ppp in oppai):
                fans[ssm]["fan"]+=(1+menqing)
                fans[ssm]["yaku"].append("三色同顺")

            ##$ 三色同刻**->2f
            if any((len(ppp)==3 and ppp[0]!=ppp[1] and ((ppp[0]+9,ppp[0]+10,ppp[0]+11,) in oppai or (1,ppp[0]+9,ppp[0]+10,ppp[0]+11,) in oppai) and ((ppp[0]+18,ppp[0]+19,ppp[0]+20,) in oppai or (1,ppp[0]+18,ppp[0]+19,ppp[0]+20,) in oppai)) or (len(ppp)==4 and ppp[0]==1 and ((ppp[1]+9,ppp[1]+10,ppp[1]+11,) in oppai or (1,ppp[1]+9,ppp[1]+10,ppp[1]+11,) in oppai) and ((ppp[1]+18,ppp[1]+19,ppp[1]+20,) in oppai or (1,ppp[1]+18,ppp[1]+19,ppp[1]+20,) in oppai)) for ppp in oppai):

                fans[ssm]["fan"]+=2
                fans[ssm]["yaku"].append("三色同刻")

            
            ##$ 对对**->2f
            
                ##$ 混老头
                if "对对和" in fans[ssm]["yaku"] and "混全带幺九" in fans[ssm]["yaku"]:
                    fans[ssm]["yaku"].append("混老头")
                    fans[ssm]["yaku"].remove("混全带幺九")
                    if not menqing:
                        fans[ssm]["fan"]+=1
                    
            
            ##$ 三暗刻**->2f

            ##$ 平和**->1fm
            if len(furu)==0:
                pass
                
            ##$ 一杯口**->1fm
        



        if result["fu"]==0:
            result["fan"]=result["fan"]//100*100
            result["yaku"]=[i for i in result["yaku"] if i in ["国士无双","国士无双十三面","字一色","四暗刻单骑","四暗刻","九莲宝灯","纯正九莲宝灯","大四喜","小四喜","大三元","绿一色","清老头","四杠子"]]
            
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