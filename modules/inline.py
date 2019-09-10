from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent
from pony.orm import db_session


@db_session
def inlineResults(user, query):
    from pony.orm import select
    from modules.database import Clip
    if query:
        selectPool = select(c for c in Clip if ((c.user == user) and ((query in c.title) or (query in c.text))))[:25]
    else:
        selectPool = select(c for c in Clip if c.user == user)[:25]
    results = []
    for clip in selectPool:
        results.append(
            InlineQueryResultArticle(
                id=str(clip.id),
                title=clip.title,
                input_message_content=InputTextMessageContent(
                    message_text=clip.text
                )))
    return results
