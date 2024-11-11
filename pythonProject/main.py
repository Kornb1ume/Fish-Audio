from khl import Bot, Message
from openai import OpenAI
import yaml
import os
import httpx
import json

# 特定语句与回复的映射
special_responses = {
    "drop_database_BRAIN": {"type": "json", "content": "BRAIN已移除_"},
    "help": {"type": "json", "content": "输入/yuuka 以进行用户聊天，输入/yuuka pub以进行公共聊天"},
    "如何评价": {"type": "json", "content": "......感觉不如@Kornb1ume"},
    "我喜欢你": {"type": "json", "content": "傻逼"},
}

# KOOK BOT
bot = Bot(token='1/MjY1NDE=/Y/iEeBSiAgn8qgmNqv8XJw==')


# -------------------帮助指令-------------------
with open('json/help.json') as file:
    data_help = json.load(file)
@bot.command(name='h')
async def help_command(msg: Message, *command):
    await msg.reply(data_help)
    return


# -------------------卡片-------------------
with open('json/card.json') as file:
    data = json.load(file)
@bot.command(name='list')
async def list_command(msg: Message, *command):
    await msg.reply(data)
    return

# ChatGPT
client = OpenAI(
    base_url="https://api.xty.app/v1",
    api_key="sk-sgaiQsLX7BdJrMpkE2C996F0838b460b84207fCfA3516106",
    http_client=httpx.Client(
        base_url="https://api.xty.app/v1",
        follow_redirects=True,
    ),
)
@bot.command(name='yuuka')
async def yuuka_command(msg: Message, *command):
    # 检查是否是用户专属聊天
    if 'pub' in command:
        # 不是专属聊天拿频道ID作为文件名
        ChatFile = 'ChatRecord/chat-' + msg.target_id + '.yaml'
        chat = command[1]
    elif command:
        # 专属聊天拿用户的ID作为文件名
        ChatFile = 'ChatRecord/chat-' + msg.extra['author']['id'] + '.yaml'
        chat = command[0]
    else:
        await msg.reply('do sth plz.')
        return

    # 检查是否有特定语句
    if chat in special_responses:
        response = special_responses[chat]
        if response["type"] == "json":
            # 发送预设的文本回复
            await msg.reply(response["content"])
            return
        elif response["type"] == "image":
            # 发送预设的图片
            if os.path.exists(response["content"]):
                with open(response["content"], 'rb') as image_file:
                    await msg.reply(file=image_file)
                return
            else:
                await msg.reply("Pic_path_does_not_exist_")
                return

    # 判断聊天记录文件，生成以及存取
    if os.path.exists(ChatFile):
        with open(ChatFile, 'r', encoding='utf-8') as getTalk:
            data = yaml.safe_load(getTalk)
            # 新建的文件获取到的getTalk会为空，需要处理一下
            talk = data if data else []
    else:
        # 新建文件
        open(ChatFile, 'w').close()
        talk = []

    LatestChat = {"role": "user", "content": chat}

    # 存入ChatRecord
    ChatRecord = talk if len(talk) < 20 else talk[-20:]

    # 往聊天记录添加刚收到的消息
    ChatRecord.append(LatestChat)

    # 调用API
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=ChatRecord
    )

    # 回复信息
    await msg.reply(completion.choices[0].message.content)

    # 往聊天记录文件里追加最新的消息
    with open(ChatFile, 'a', encoding='utf-8') as writeTalk:
        yaml.dump([LatestChat], writeTalk, allow_unicode=True, default_flow_style=False)

bot.run()

