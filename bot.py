import telepot
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent
from tinydb import TinyDB, where
from time import sleep

# Load the bot
try:
    # Try to read the token
    token_file = open('bot_token.txt', 'r')
    bot_token = token_file.readline().strip()
    bot = telepot.Bot(bot_token)
    token_file.close()
except FileNotFoundError:
    # Ask the user for the token
    token_file = open('bot_token.txt', 'w')
    bot_token = input("Please insert the bot token: ")
    bot = telepot.Bot(bot_token)
    token_file.write(bot_token)
    token_file.close()

# Load databases
clip_db = TinyDB('clips_database.json')
user_db = TinyDB('users_database.json')


def getUserInfo(msg):
    # Get all necessary infos from the message object
    msgType, chatType, chatId = telepot.glance(msg)
    msgId = msg['message_id']
    if chatType == "private":
        name = msg['chat']['first_name']
        if msgType == "text":
            text = msg['text']
        else:
            text = None
    else:
        name = None
        text = None
    return msgType, msgId, chatType, chatId, name, text


def getString(string, *args):
    # All strings used by the bot messages

    if string == "cmd_start":
        result = "Hi, <b>{0}</b>!\n" \
                 "Send me some text that you want to store!\n" \
                 "Press /help if you need."

    elif string == "cmd_help":
        result = "I'm the Paste and Share bot.\n" \
                 "Send me some text that you want to store, like a clipboard.\n" \
                 "You can later search for any text you sent here, with:\n\n" \
                 "- /clip 'ClipCode' (you'll get this code by sending a text to the bot)\n" \
                 "- Via inline chat, for example in a group, with <i>@pasteandsharebot 'ClipCode'</i>\n\n" \
                 "Other commands:\n" \
                 "/start - Start the bot\n" \
                 "/help - Show this message" \
                 "/clip 'ClipCode'- Search Clips (read infos up)\n" \
                 "/list - Show a list of all your saved clips\n" \
                 "/delete 'ClipCode' - Delete a clip\n" \
                 "/edit 'ClipCode' - Edit a clip"

    elif string == "not_text_message":
        result = "Sorry, I can only store text messages at the moment.\n" \
                 "Need /help?"

    elif string == "feature_not_available":
        result = "Sorry, at the moment this feature is not available. Try later.\n" \
                 "Need /help?"

    elif string == "clip_no_arg":
        result = "Sorry, you must specify a ClipCode.\n" \
                 "Need /help?"

    elif string == "edit_no_arg":
        result = "Sorry, you must specify a ClipCode.\n" \
                 "Need /help?"

    elif string == "delete_no_arg":
        result = "Sorry, you must specify a ClipCode.\n" \
                 "Need /help?"

    elif string == "message_saved":
        result = "<b>Message Saved!</b>\n" \
                 "ClipCode: <code>{0}</code>"

    elif string == "get_clip":
        result = "Here's what I found:\n\n" \
                 "{0}"

    elif string == "get_clip_empty":
        result = "Sorry, you have not saved any clip matching the query '{0}'\n" \
                 "Need /help?"

    elif string == "inline_title_clip_notfound":
        result = "Clip Not Found"

    elif string == "inline_text_clip_notfound":
        result = "Error: Clip not found"

    elif string == "inline_title_clip_result":
        result = "Clip #{0}"

    elif string == "list_head":
        result = "Here's a list of all your clips:{0}"

    elif string == "list_body":
        result = "\n\nClip #{0}:\n{1}"

    elif string == "list_empty":
        result = "You have not saved any clip, at the moment."

    elif string == "removed_clip":
        result = "Successfully deleted clip #{0}"

    elif string == "edited_clip":
        result = "Successfully edited clip #{0}"

    elif string == "cancel":
        result = "Operation aborted."

    elif string == "confirm_delete":
        result = "Are you sure you want to permanently delete clip #{0}?\n" \
                 "Type 'Yes' to confirm or '/cancel' to abort."

    elif string == "confirm_edit":
        result = "Now send me the new text for clip {0}.\n" \
                 "Type '/cancel' to abort."

    else:
        result = "Not Found"

    return result.format(*args)


def insertData(user_id, clip_code, data):
    # Insert a clip into the database
    clip_db.insert({'chatId': user_id, 'clipCode': clip_code, 'data': data})


def updateUser(user_id, addClip=True, status="normal"):
    # If the user is already registered, update infos
    if user_db.search(where('chatId') == user_id):
        # Update clips
        if addClip:
            prev_tclips = user_db.search(where('chatId') == user_id)[0]['totalClips']
            user_db.update({'totalClips': prev_tclips+1, 'status': status}, where('chatId') == user_id)
            return prev_tclips + 1
        # Update status
        else:
            user_db.update({'status': status}, where('chatId') == user_id)

    # Else, add the user with default data
    else:
        user_db.insert({'chatId': user_id, 'totalClips': 1, 'status': "normal"})
        return 1


def on_message(msg):
    # Get the infos
    msgType, msgId, chatType, chatId, name, text = getUserInfo(msg)

    if chatType == "private":

        if msgType == "text":
            # Get the user status
            try:
                userStatus = str(user_db.search(where('chatId') == chatId)[0]['status'])
            except KeyError:
                userStatus = "normal"

            if text == "/cancel":
                updateUser(chatId, addClip=False, status="normal")
                bot.sendMessage(chatId, getString("cancel"))

            elif userStatus.startswith("deleting#"):
                if text == "Yes":
                    to_delete = userStatus.split("#", 1)[1]
                    clip_db.remove(where('clipCode') == int(to_delete))
                    updateUser(chatId, addClip=False, status="normal")
                    bot.sendMessage(chatId, getString("removed_clip", to_delete))
                else:
                    updateUser(chatId, addClip=False, status="normal")
                    bot.sendMessage(chatId, getString("cancel"))

            elif userStatus.startswith("editing#"):
                to_edit = userStatus.split("#", 1)[1]
                clip_db.update({'data': text}, where('clipCode') == int(to_edit))
                updateUser(chatId, addClip=False, status="normal")
                bot.sendMessage(chatId, getString("edited_clip", to_edit))

            elif text == "/start":
                bot.sendMessage(chatId, getString("cmd_start", name), "HTML")

            elif text == "/help":
                bot.sendMessage(chatId, getString("cmd_help"), "HTML")

            elif text == "/clip":
                bot.sendMessage(chatId, getString("clip_no_arg"))

            elif text == "/edit":
                bot.sendMessage(chatId, getString("edit_no_arg"))

            elif text == "/delete":
                bot.sendMessage(chatId, getString("delete_no_arg"))

            elif text == "/list":
                clips = clip_db.search(where('chatId') == chatId)
                if clips != []:
                    data = ""
                    for clip in clips:
                        data += getString("list_body", clip['clipCode'], clip['data'])
                    bot.sendMessage(chatId, getString("list_head", data))
                else:
                    bot.sendMessage(chatId, getString("list_empty"))


            elif text.startswith("/clip "):
                query = text.split(" ", 1)[1]
                try:
                    data = clip_db.search((where('chatId') == chatId) & (where('clipCode') == int(query)))[0]['data']
                    if data != "":
                        bot.sendMessage(chatId, getString("get_clip", data))
                    else:
                        bot.sendMessage(chatId, getString("get_clip_empty", query))
                except (IndexError, ValueError):
                    bot.sendMessage(chatId, getString("get_clip_empty", query))

            elif text.startswith("/delete "):
                query = text.split(" ", 1)[1]
                updateUser(chatId, addClip=False, status="deleting#"+query)
                bot.sendMessage(chatId, getString("confirm_delete", query))

            elif text.startswith("/edit "):
                query = text.split(" ", 1)[1]
                updateUser(chatId, addClip=False, status="editing#"+query)
                bot.sendMessage(chatId, getString("confirm_edit", query))


            # If the message is not a recognized command, add it as a clip
            else:
                clipCode = updateUser(chatId)
                insertData(chatId, clipCode, text)
                bot.sendMessage(chatId, getString("message_saved", clipCode), "HTML")

        # If the message is not a text
        else:
            bot.sendMessage(chatId, getString("not_text_message"), "HTML")


def on_inline_query(msg):
    # Get the infos
    query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
    try:
        data = clip_db.search((where('chatId') == from_id) & (where('clipCode') == int(query_string)))[0]['data']
        if data != "":
            article = InlineQueryResultArticle(
                id=query_string,
                title=getString("inline_title_clip_result", query_string),
                input_message_content=InputTextMessageContent(
                    message_text=data
                )
            )
        else:
            article = InlineQueryResultArticle(
                id='error',
                title=getString("inline_title_clip_notfound"),
                input_message_content=InputTextMessageContent(
                    message_text=getString("inline_text_clip_notfound")
                )
            )
    except (IndexError, ValueError):
        article = InlineQueryResultArticle(
            id='error',
            title=getString("inline_title_clip_notfound"),
            input_message_content=InputTextMessageContent(
                message_text=getString("inline_text_clip_notfound")
            )
        )

    choices = [article]
    bot.answerInlineQuery(query_id, choices, cache_time=10, is_personal=True, next_offset="")


# Keep alive the bot
bot.message_loop({'chat': on_message, 'inline_query': on_inline_query})
print("Bot started...")
while 1:
    sleep(60)
