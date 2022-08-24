import asyncio
import io
import typing
import discord

import utils

from discord.ext import commands


class ConvenienceHandler(commands.Cog, name='Convenience'):
    """Handles all convenience commands and features of the bot"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="makehungergames", aliases=['mkhg'])
    async def make_hunger_games(self, ctx:commands.Context, *, flags:utils.HungerGamesFlags):
        """Makes a BrantSteele Hunger Games Simulator cast text file from server members. Learn more about the Hunger Game Simulator here: https://brantsteele.com/hungergames/classic/reaping.php
        
        There are two ways to use this command: You can specify the members to include using the -members flag, or you can run the command while replying to a post that has reactions of people who want to be included. In the latter case, you must specify the reaction using the -reaction flag. You can also combine the two modes!
        
        Flags:
        -imagechannel: Required; Text Channel; The text channel where the members' profile pics will be posted (this is necessary for the Simulator to use Profile Pictures).
        -members: Optional; Server Member; Members to include in the hunger games. If this is specified, then the order of the provided members is the order they will be included in the districts.
        -reaction: Optional; Emote; The reaction to use.
        -usemembernicknames: Optional; True or False; Whether to use server members nicknames or their Discord tags. Default False (use Discord tags).
        -useserveravatars: Optional; True or False; For Nitro members, Whether to use server-specific profile pictures or their standard Discord profile picture. Default True (use server-specific profile picture).
        """
        members_from_reaction = list()
        if flags.imagechannel is None:
            await ctx.reply("No text channel was provided to post the discord profile pictures!")
            return
        if not flags.imagechannel.permissions_for(ctx.author).attach_files: #Command caller can not send messages in specified channel
            await ctx.reply("The text channel you provided is not a channel that you can send messages in!")
            return
        if ctx.message.reference is not None:
            if flags.reaction is None:
                await ctx.reply("You replied to a message but did not specify a reaction to use!")
                return
            replied_message:discord.Message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            reaction:typing.Union[discord.Reaction, None] = discord.utils.find(lambda x: x.emoji == flags.reaction, replied_message.reactions)
            if reaction is None:
                await ctx.reply("The specified reaction was not found in the message you replied to!")
                return
            members_from_reaction:typing.List[discord.Member] = [member async for member in reaction.users()]
        if flags.members is None and ctx.message.reference is None:
            await ctx.reply("No members specified!")
            return
        if flags.members is not None:
            members = list(flags.members) + members_from_reaction
            unique_members:typing.List[discord.Member] = list(set(members))
        else:
            unique_members = members_from_reaction
        config:io.StringIO = io.StringIO()
        config.write("The Hunger Games\nhttps://brantsteele.com/extras/hungergames/01/logo.png")
        size:int = len(unique_members)
        district_number:int = 1 #initial value
        for i in range(size): #starts at i=0, last index at i=size-1
            member = unique_members.pop()
            avatar:discord.Asset = utils.get_avatar(member, flags.useserveravatars)
            avatar:discord.File = discord.File(io.BytesIO(await avatar.read()), filename=f"{member.id}.png")
            name:str = utils.get_name(member, flags.usemembernicknames)
            image_message:discord.Message = await flags.imagechannel.send(file=avatar)
            avatar_url:str = image_message.attachments.pop().url
            if not i % 2: #If index is even, meaning 1st district member
                config.write(f"\n\n\nDistrict {district_number}\n#ffffff 0 0\n\n{name}\n{name}\n1\n{avatar_url}\nBW")
            else: #If index is odd, meaning the 2nd district member
                config.write(f"\n\n{name}\n{name}\n0\n{avatar_url}\nBW")
                district_number += 1
        if not size % 2: #if even number of members
            district_number -= 1
        config.seek(0)
        odd_clause = ""
        if size % 2:
            odd_clause += f" Because there was a total of {size} participants, District {district_number} has only 1 member."
        await ctx.reply(f"BrantSteele Hunger Games Simulator cast file complete! There are {district_number} district(s) in this hunger games, with 2 member(s) per district.{odd_clause}", file=discord.File(config, filename="cast.txt"))
