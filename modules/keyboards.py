from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from pony.orm import db_session


@db_session
def delete(user, msg_id):
    from pony.orm import select
    from modules.database import Clip
    keyboard = []
    line = []
    linecount = 0
    for clip in select(c for c in Clip if c.user == user)[:]:
        linecount += 1
        if linecount > 2:
            linecount = 1
            keyboard.append(line)
            line = []
        line.append(InlineKeyboardButton(text=clip.title, callback_data="delclip_{}#{}".format(clip.id, msg_id)))
    if line:
        keyboard.append(line)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def delete_confirm(clip_id, msg_id):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Yes", callback_data="deleteyes_{}#{}".format(clip_id, msg_id)),
        InlineKeyboardButton(text="🔴 No!", callback_data="deleteno#{}".format(msg_id)),
    ]])
