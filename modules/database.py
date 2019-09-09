from pony.orm import Database, Required, Optional, Set

db = Database("sqlite", "../clipsharebot.db", create_db=True)


class User(db.Entity):
    chatId = Required(int, unique=True)
    status = Required(str, default="normal")
    clips = Set(lambda: Clip, reverse='user')


class Clip(db.Entity):
    user = Required(User)
    title = Required(str, default="Clip")
    text = Required(str, default="No Text")


db.generate_mapping(create_tables=True)
