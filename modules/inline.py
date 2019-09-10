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
        cliptext = " ".join(clip.text.split()[:10])
        cliptext = cliptext if len(clip.text.split()[:10]) < 11 else cliptext + "..."
        results.append(
            InlineQueryResultArticle(
                id=str(clip.id),
                title=clip.title,
                input_message_content=InputTextMessageContent(
                    message_text=cliptext
                )))
    return results
