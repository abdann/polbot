import asyncio
import io
import json
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
        """Makes a Agma Schwa Hunger Games Simulator cast JSON file from server members. Learn more about the Hunger Game Simulator here: https://www.nguh.org/tools/hunger_games_simulator
        
        There are two ways to use this command: You can specify the members to include using the -members flag, or you can run the command while replying to a post that has reactions of people who want to be included. In the latter case, you must specify the reaction using the -reaction flag. You can also combine the two modes!
        
        Flags:
        -members: Optional; Server Member; Members to include in the hunger games. If this is specified, then the order of the provided members is the order they will be included in the districts.
        -reaction: Optional; Emote; The reaction to use.
        -usemembernicknames: Optional; True or False; Whether to use server members nicknames or their Discord tags. Default False (use Discord tags).
        -useserveravatars: Optional; True or False; For Nitro members, Whether to use server-specific profile pictures or their standard Discord profile picture. Default True (use server-specific profile picture).
        """
        members_from_reaction = list()
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
        cast = {"characters" : list()}
        for member in unique_members:
            entry:typing.Dict[str, str] = {
                "name" : utils.get_name(member, flags.usemembernicknames),
                "gender_select" : "n",
                "custom_pronouns" : "",
                "image" : utils.get_avatar(member, flags.useserveravatars).url
            }
            cast.get("characters").append(entry)
        file:io.StringIO = io.StringIO()
        json.dump(cast, file)
        file.seek(0)
        await ctx.reply(
            f'Agma Schwa Hunger Games JSON cast file complete! Head to `https://www.nguh.org/tools/hunger_games_simulator` and upload this file using the "Load Characters" button to load the cast.',
            file=discord.File(file, filename="hgsimulator-setup.json")
            )