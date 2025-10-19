import discord
import random

#カレントディレクトリからの相対パス
path = r"Downloads\toeic_bot\toeic_input.txt"
path2= r"Downloads\toeic_bot\toeic_memorized.txt"


TOKEN="test" #TOKENを張り付け
CHANNELID = 1234 #channel ID を張り付け 

client = discord.Client(intents=discord.Intents.all())


@client.event
async def on_ready():
    print('ログインしました')
    channel = client.get_channel(CHANNELID)
    await channel.send("こんにちは")
    
#client.run(TOKEN)



"""
#フォーマット
@client.event
async def on_message(message):
    if not message.author.bot:
        channel = client.get_channel(CHANNELID)
        S=message.content
        print(type(S))
        L=list(map(str,S.split()))#リスト化したいとき
        await channel.send("対象")
        print(message.content)

#client.run(TOKEN)
#フォーマット終わり
"""


gold_phrase=dict()


def multiple_split(S):
    L=S.split()
    ans=[]
    now=""
    for l in L:
        for s in l:
            if s in ["、",","]:
                ans.append(now)
                now=""
            else:
                now+=s
        ans.append(now)
        now=""        
    ans1=[]
    ans2=[]
    f=0
    for a in ans:
        if a[0]=="[":
            f=1
        if f==0:
            ans1.append(a)
        else:
            ans2.append(a)
    return ans1,ans2


idx=0
mode_list=["600点","730点","860点","990点","パート1重要語","部署・職業・学問","前置詞・接続詞","**多義語**","定型表現"]
mode_dict=dict()

#単語を追加(txtで)
with open(path,encoding="utf-8") as f:
    L = [s.rstrip() for s in f.readlines()]
    #print(L)
for S in L:
    if S=="ちぇんじ":
        idx+=1
        continue
    ph=" ".join(multiple_split(S)[0])
    tr=multiple_split(S)[1]
    gold_phrase[ph]=tr
    mode_dict[ph]=idx

#print(gold_phrase)
unmemorized=[]

with open(path2,encoding="utf-8") as f:
    memorized = set([s.rstrip() for s in f.readlines()])
    

for k in gold_phrase.keys():
    if k not in memorized:
        unmemorized.append(k)

#print(unmemorized)
cnt_all=len(gold_phrase)
cnt_memorized=len(memorized)

#ランダムな英語フレーズと日本語訳を取得
def get_random_phrase():
    if unlearned==1:
        return random.choice(unmemorized)
    else:
        return random.choice(list(gold_phrase.keys()))

cnt_today=0
#英語フレーズと、スポイラーされた日本語訳を表示
@client.event
async def show_english_phrase(message):
    global cnt_today
    global ph
    global tr_list
    channel = client.get_channel(CHANNELID)
    if unlearned==1 and cnt_memorized==cnt_all:
        await channel.send("すでに全ての単語を覚えています")
        return
    ph = get_random_phrase()
    tr_list=gold_phrase[ph]
    cnt_today+=1
    await channel.send("{}問目  {}/{}を暗記済み".format(cnt_today,cnt_memorized,cnt_all))
    await channel.send("**{}** ({})".format(ph,mode_list[mode_dict[ph]]))
    for tr in tr_list:
        if tr[0]=="[":
            await channel.send("{}||{}||".format(tr[:3],tr[3:]))
        else:
            await channel.send("||{}||".format(tr))

#tを押したときに日本語訳を表示
@client.event
async def show_japanese_translation(message):
    channel = client.get_channel(CHANNELID)
    for tr in tr_list:
        await channel.send(tr)  
        

#覚えた単語をファイルに記録する(、cnt_memorized増やす、unmemorizedから消す.※毎回O(N)だけどN=10^3くらいだから許される)→次の単語に行く
@client.event
async def memorizing_ok(message):
    if unlearned==0:
        return
    global cnt_memorized
    global memorized
    channel = client.get_channel(CHANNELID)
    memorized.add(ph)
    with open(path2, mode='w',encoding="utf-8") as f:
        f.write('\n'.join(memorized))
    await channel.send("**{}**を覚えました！".format(ph))
    unmemorized.remove(ph)
    cnt_memorized+=1
    if unlearned==1 and cnt_memorized==cnt_all:
         await channel.send("全ての単語を覚えました！おつかれさまでした！")
    await show_english_phrase(message)



#delete→yesで記録を消去
delete=0
@client.event
async def delete_memorized_phrase(message):
    global delete
    channel = client.get_channel(CHANNELID)
    await channel.send("全ての記録を消しますか？yesと入力すると実行します")
    delete=1

@client.event
async def delete_memorized_phrase_confirmed(message):
    global delete
    global cnt_memorized
    channel = client.get_channel(CHANNELID)
    if delete==1:
        if message.content=="yes":
            with open(path2, mode='w') as f:
                f.write("")
            cnt_memorized=0
            unmemorized=list(gold_phrase.keys())
            await channel.send("記録が消去されました")
            delete=0
        else:
            await channel.send("消去はキャンセルされました")
            delete=0        

#モードを変える(デフォルトはunlearned=1)
unlearned=1
@client.event
async def change_mode(message):
    global unlearned
    channel = client.get_channel(CHANNELID)
    if message.content=="all":
        unlearned=0
        await channel.send("全ての収録単語から出題します")
    if message.content=="yet":
        unlearned=1
        await channel.send("まだ覚えていない単語から出題します")
   

#コマンド処理
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    channel = client.get_channel(CHANNELID)
    #S=message.content
    if message.content.startswith("p"):#\だった
        await show_english_phrase(message)
    if message.content.startswith("t"):
        await show_japanese_translation(message)
    if message.content=="ok":
        await memorizing_ok(message)
    if message.content=="delete":
        await delete_memorized_phrase(message)
    if message.content=="yes":
        await delete_memorized_phrase_confirmed(message)
    if message.content in ["all","yet"]:
        await change_mode(message)
    if message.content=="f":    
        await message.channel.send("終了します")
        await client.close()

#botの起動
client.run(TOKEN)


