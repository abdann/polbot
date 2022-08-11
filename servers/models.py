# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Server(Base):
    __tablename__ = 'servers'

    server_id = Column(Integer, primary_key=True)


class Parameter(Server):
    __tablename__ = 'parameters'

    server_id = Column(ForeignKey('servers.server_id', ondelete='CASCADE'), primary_key=True)
    min_account_age = Column(Integer, nullable=False)
    new_auto_ban = Column(Integer, nullable=False)
    lockdown = Column(Integer, nullable=False)
    polder_channel_id = Column(Integer)
    polder = Column(Integer, nullable=False)
    random_polder_posts = Column(Integer, nullable=False)
    random_text_posts = Column(Integer, nullable=False)
    shitpost_probability = Column(Integer, nullable=False)


class AutoBanWhitelist(Base):
    __tablename__ = 'auto_ban_whitelist'

    server_id = Column(ForeignKey('servers.server_id', ondelete='CASCADE'), primary_key=True, nullable=False)
    user_id = Column(Integer, primary_key=True, nullable=False)

    server = relationship('Server')


class EmojiTrigger(Base):
    __tablename__ = 'emoji_triggers'

    server_id = Column(ForeignKey('servers.server_id', ondelete='CASCADE'), primary_key=True, nullable=False)
    trigger_phrase = Column(Text, primary_key=True, nullable=False)
    emoji = Column(Text, primary_key=True, nullable=False)

    server = relationship('Server')


class Polder(Base):
    __tablename__ = 'polder'

    server_id = Column(ForeignKey('servers.server_id', ondelete='CASCADE'), nullable=False)
    message_id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer)
    channel_id = Column(Integer, nullable=False, server_default=text("923301521356116087"))

    server = relationship('Server')


class ShitpostingChannel(Base):
    __tablename__ = 'shitposting_channels'

    server_id = Column(ForeignKey('servers.server_id', ondelete='CASCADE'), nullable=False)
    channel_id = Column(Integer, primary_key=True)

    server = relationship('Server')


class TextTrigger(Base):
    __tablename__ = 'text_triggers'

    server_id = Column(ForeignKey('servers.server_id', ondelete='CASCADE'), primary_key=True, nullable=False)
    trigger_phrase = Column(Text, primary_key=True, nullable=False)
    message = Column(Text, primary_key=True, nullable=False)

    server = relationship('Server')
