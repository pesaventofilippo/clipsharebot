from time import sleep
from telepot import Bot, glance
from threading import Thread
from pony.orm import db_session, commit
from modules.database import User, Clip
from modules import keyboards, inline

with open('token.txt', 'r') as f:
    token = f.readline().strip()
    bot = Bot(token)


@db_session
def reply(msg):
    chatId = msg['chat']['id']
    text = msg['text']
    name = msg['from']['first_name']

    if not User.exists(lambda u: u.chatId == chatId):
        User(chatId=chatId)
    user = User.get(chatId=chatId)

    if user.status == "newclip":
        if text == "/cancel":
            user.status = "normal"
            bot.sendMessage(chatId, "❌ /newclip cancelled!")
        
        else:
            clip = Clip(user=user, text=text)
            commit()
            user.status = "cliptitle#{}".format(clip.id)
            bot.sendMessage(chatId, "✅ Clip successfully created!\n"
                                    "What title should it have?")
    
    elif user.status.startswith("cliptitle"):
        clipid = int(user.status.split("#")[1])
        clip = Clip.get(user=user, id=clipid)
        clip.title = text
        user.status = "normal"
        bot.sendMessage(chatId, "📝 Clip <b>{}</b> renamed!\n"
                                "Ready to share it? Use me in a chat by typing @clipsharebot!".format(text), parse_mode="HTML")
    
    elif user.status == "normal":
        if text == "/start":
            bot.sendMessage(chatId, "Hey, <b>{}</b>! 👋🏻\n"
                                    "Type /new to create a new custom clip.".format(name), parse_mode="HTML")
        
        elif text == "/cancel":
            bot.sendMessage(chatId, "Operation cancelled!\n"
                                    "I was doing nothing, btw... 😴")
        
        elif text == "/new" or ("newclip_inline" in text):
            user.status = "newclip"
            bot.sendMessage(chatId, "✏️ Ok, send me the text for the new clip!\nType /cancel to abort.")
        
        elif text == "/list":
            clips = user.clips
            if clips:
                message = "📚 <b>Clips List</b>\n<i>Click on a title to see the full content</i>\n"
                for clip in clips:
                    message += "\n📄 <a href=\"https://t.me/clipsharebot?start=getclip_{}\">{}</a>".format(clip.id, clip.title)
            else:
                message = "😓 Sorry, you don't have clips yet! Type /new to get started."
            bot.sendMessage(chatId, message, parse_mode="HTML", disable_web_page_preview=True)

        elif text == "/delete":
            if user.clips:
                sent = bot.sendMessage(chatId, "🗑 <b>Delete a Clip</b>\n"
                                               "What clip would you like to delete? Type /list if you want to see a clip's full content.", parse_mode="HTML")
                bot.editMessageReplyMarkup((chatId, sent['message_id']), keyboards.delete(user, sent['message_id']))
            else:
                bot.sendMessage(chatId, "😓 Sorry, you don't have clips yet! Type /new to get started.")
        
        elif text.startswith("/start getclip"):
            clipid = int(text.split("_")[1])
            clip = Clip.get(user=user, id=clipid)
            if clip:
                bot.sendMessage(chatId, "📖 <b>Open Clip</b>\n\n<b>Title:</b> {}\n<b>Text:</b> {}".format(clip.title, clip.text), parse_mode="HTML")
            else:
                bot.sendMessage(chatId, "🔒 <i>Error: this clip has been deleted.</i>", parse_mode="HTML")
        
        else:
            bot.sendMessage(chatId, "🤨 <i>Command not found.</i>", parse_mode="HTML")


@db_session
def button(msg):
    chatId, query_data = glance(msg, flavor="callback_query")[1:3]
    user = User.get(chatId=chatId)
    query_split = query_data.split("#")
    query = query_split[0]
    message_id = int(query_split[1])

    if query.startswith("delclip"):
        clipid = int(query.split("_")[1])
        clip = Clip.get(user=user, id=clipid)
        cliptext = " ".join(clip.text.split()[:10])
        cliptext = cliptext if len(clip.text.split()[:10]) < 11 else cliptext + "..."
        bot.editMessageText((chatId, message_id), "⚠️ Are you <b>totally sure</b> you want to delete this clip?\n\n"
                                                  "<b>Title:</b> {}\n"
                                                  "<b>Text:</b> {}".format(clip.title, cliptext), parse_mode="HTML", reply_markup=keyboards.delete_confirm(clipid, message_id))
    
    elif query.startswith("deleteyes"):
        clipid = int(query.split("_")[1])
        clip = Clip.get(user=user, id=clipid)
        clip.delete()
        bot.editMessageText((chatId, message_id), "🗑 Clip successfully deleted!", reply_markup=None)
    
    elif query == "deleteno":
        bot.editMessageText((chatId, message_id), "👍 Clip restored!", parse_mode="HTML", reply_markup=None)


@db_session
def inline(msg):
    queryId, chatId, queryString = glance(msg, flavor='inline_query')
    user = User.get(chatId=chatId)
    results = inline.inlineResults(user, queryString)
    bot.answerInlineQuery(queryId, results, cache_time=10, is_personal=True,
                            switch_pm_text="Create a new Clip", switch_pm_parameter="newclip_inline")


def incoming_message(msg):
    Thread(target=reply, args=[msg]).start()

def incoming_button(msg):
    Thread(target=button, args=[msg]).start()

def incoming_query(msg):
    Thread(target=inline, args=[msg]).start()

bot.message_loop({'chat': incoming_message, 'callback_query': incoming_button, 'inline_query': incoming_query})
while True:
    sleep(60)
