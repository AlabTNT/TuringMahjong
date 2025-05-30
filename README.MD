# Turing Mahjong

如你所见，现在这个仓库仍然处于一个正在更新的状态。还没有发布版本。

目前希望这个软件可以发布到多平台，但是因为技术力原因还没能成功打包apk，因此只好暂时放弃全平台。

由于没有发布版本，非开发者请勿下载！

使用雀魂（Mahjong-Soul）素材，禁止商用


## 游戏算法公示

由于麻将游戏具有随机性，在线下麻将时部分人可以通过控制随机性来破坏游戏平衡（俗称“出老千”），线上麻将亦是如此。为了证明本游戏没有为开发者或阅读过开源代码者提供便利以获得某局游戏的剩余牌山，或为连续和牌者提供不利于牌局的牌，或为运气较差者提供利于牌局的牌（“杀熟”和“保底”），特在此公示本游戏牌山随机算法。（实际实现详见server.py:MahjongGame.generate_mountain）

生成牌山时，首先不指定种子的情况下随机n的值为1~100，然后执行n次随机，每次选取1~100的值，之后求和这些随机值，取该值的字符串。后接本局游戏全部玩家的client（包含旁观者）的list的hash值的字符串（list内存client实例地址，由python动态分配），最后接生成牌山时的时间字符串。获得字符串后，求取其sha256值，以此值为种子，对按顺序排好的牌山进行shuffle操作，得到初始牌山。

初始牌山生成结束后，每34张牌作为一座，共四座山，代表东南西北四家面前的牌山。之后按种子取两次random.randint确定初始位置（0=东家，1=南家，以此类推），再获取两次random.randint确定牌尾。牌尾L确定方式是前两次两次random.randint值相加模4后乘34再加后两次random.randint相加乘2。index=L的牌作为牌山起始摸牌点，index=L-1~L-14作为王牌，index=L-10作为初始宝牌指示牌，以此类推（例如第二张里宝牌index=L-7，第一张岭上牌index=L-14，海底牌index=L-15）。为了方便，将牌山L之后的牌全部提前到最开始，即所有牌的index-=L，得到最终牌山。

得到最终牌山后，计算sha256值并予以公示，玩家可在对局结束后验证该sha256值是否正确。（由于sha256不可逆，只能在获得牌山后才可验证）。

## 开发者提示

git clone后，使用`./update.bat "<Version>" "<Description>"`来更新自己的内容。

在tips/文件夹下创建属于自己的.txt，然后在该文件下添加自己的提示，例如如何使用自己写的文件等等。管理员会在合适的时机处理你的.txt并合并进本.md。

> **Version使用规范：**  
> ReleaseX.Y.Z 发布版，用于发布内容。bug修复更新时Z+1；内容/功能更新时Y+1；整体重构或更新架构时X+1。起始为1.0.0  
> BetaX.Y 公测版，用于发布可供广泛测试的测试版。每个Alpha版更新为Beta版时Y+1；每个Alpha版迭代时X+1。起始为0.0.  
> AlphaX.Y 内测版，用于发布供发布者测试的测试版。修复或内容功能调整时Y+1；每个Dev版更新为Alpha版时X+1。起始为0.0.  
> DevXXwYYaZZZ.NNNN 开发版，用于开发者每次开发周期结束时推送仓库。XX为年份，YY为学期+周（0=春；1=夏；2=暑；3=秋；4=冬；5=寒。例如22a代表暑学期第二周），ZZZ为迭代次数（001开始），NNNN为开发者代号。不在开发者列表中的请署名ctbr.xxxx（xxxx请自行决定内容，也可留空为匿名）  


**开发者列表**

- AlabTNT: atnt
- jayi0908: jayi
- MoonCake__MC: ybmc
- shang: shng

***请开发者务必及时更新.gitignore! ***
