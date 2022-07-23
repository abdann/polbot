from string import punctuation
import discord
import cogs.permissionshandler
from discord.ext import commands
from random import random, sample
import re
import markovify
import utils
from os import walk
from pathlib import Path
import aiofiles
import asyncio


punctuation = [".", "?", "!"]
mute_all_pings = discord.AllowedMentions(everyone=False, users=False, roles=False, replied_user=False)
mute_role_and_everyone_pings = discord.AllowedMentions(everyone=False, users=True, roles=False, replied_user=True)

class ShitpostingHandler(commands.Cog, name='Shitposting'):
    """Handles all shitposting commands and features of the bot"""
    def __init__(self, bot):
        self.bot = bot
        self.bot.making_text = False
        self.RE_MESSAGE_MATCH = '^[a-zA-Z0-9\s\.,“”!\?/\(\)]+$'

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        params = await self.bot.servers.get_server_parameters(message.guild, "a")
        if await self.bot.servers.find_in_shitposting_channels(message.guild, message.channel.id):
            if self.bot.user.mentioned_in(message):
                await self._post_random_text(message, params)
            await self._post_listener(message, params, self._post_random_polder)
            await self._post_listener(message, params, self._post_random_text)
        await self._add_polder_post(message, params)

    @commands.command(name="setpolderhere", aliases=['setpolder'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def set_polder_here(self, ctx):
        """[Default Admin command] Sets the polder channel to the current channel. All images and text posted in the polder channel will have a chance to be randomly posted in the allowed channels. This is separate from the randomly generated text posting."""
        params = await self.bot.servers.get_server_parameters(ctx.guild, "polder_channel_id")
        params.update({"polder_channel_id":ctx.channel.id})
        await self.bot.servers.update_server_parameters(ctx.guild, **params)
        await ctx.reply(f"Set the polder channel to #{ctx.channel.name}")

    @commands.command(name="enablepolder", aliases=['epolder'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def enable_polder(self, ctx):
        """[Default Admin command] Enables polder image collection. Use this if you want PolBot to save text and images from polder."""
        params = await self.bot.servers.get_server_parameters(ctx.guild, "polder")
        if params.get("polder"):
            await ctx.reply("Polder image collection is already enabled.")
            return
        params.update({"polder":True})
        await self.bot.servers.update_server_parameters(ctx.guild, **params)
        await ctx.reply("Polder image collection is now enabled.")

    @commands.command(name="disablepolder", aliases=['dpolder'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def disable_polder(self, ctx):
        """[Default Admin command] Disables polder content collection. Use this if you want to prevent PolBot from saving text and images from polder, for whatever reason."""
        params = await self.bot.servers.get_server_parameters(ctx.guild, "polder")
        if not params.get("polder"):
            await ctx.reply("Polder image collection is already disabled.")
            return
        params.update({"polder":False})
        await self.bot.servers.update_server_parameters(ctx.guild, **params)
        await ctx.reply("Polder image collection is now disabled.")

    @commands.command(name="removepolderpost", aliases=['rmpolderpost'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def remove_polder_post(self, ctx):
        """[Default Mod command] When this command is run in a reply to a polder post posted by PolBot, it removes the polder post from PolBot's memory."""
        params = await self.bot.servers.get_server_parameters(ctx.guild, "polder_channel_id")
        if ctx.message.reference is None:
            await ctx.reply("You did not reply to a message while running this command!")
            return
        posted_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        if ctx.channel.id == params.get("polder_channel_id"): #if we are in polder channel
            if posted_message.author.id != self.bot.user.id: #If the posted message to remove was not posted by the bot
                uploaded_media_link_list = [attachment.url for attachment in posted_message.attachments]
                uploaded_media_links = "\n".join(uploaded_media_link_list) if len(uploaded_media_link_list) > 0 else ""
                content = posted_message.content + "\n" + uploaded_media_links if uploaded_media_links != "" else posted_message.content
                if await self.bot.servers.remove_in_polder(ctx.guild, content=content):
                    await ctx.reply("I won't post *that* ever again ;)")
                    return
                else:
                    await ctx.reply("I don't remember having *that* saved (I may be having a stroke, please call my master)")
                    return
            else:
                await ctx.reply("The message you replied to is not something *I* posted, you twat.")
                return
        else: #we are in a shitposting channel
            if posted_message.author.id == self.bot.user.id: #if the posted message to remove was posted by polbot
                if await self.bot.servers.remove_in_polder(ctx.guild, content=posted_message.content):
                    await ctx.reply("I won't post *that* ever again ;)")
                    return
                else:
                    await ctx.reply("I don't remember having *that* saved (I may be having a stroke, please call my master)")
                    return
            else:
                await ctx.reply("The message you replied to is not something *I* posted, you twat.")
                return

    
    async def _add_polder_post(self, message:discord.Message, params):
        """Adds a message to PolBot's repetoire of things he can post from polder."""
        if message.channel.id == params.get("polder_channel_id") and params.get("polder"):
            if message.content.startswith(self.bot.command_prefix): # Exit if contains command
                return
            if message.author.id == self.bot.user.id: # Exit if bot message
                return
            uploaded_media_link_list = [attachment.url for attachment in message.attachments]
            uploaded_media_links = "\n".join(uploaded_media_link_list) if len(uploaded_media_link_list) > 0 else ""
            content = message.content + "\n" + uploaded_media_links if uploaded_media_links != "" else message.content
            await self.bot.servers.add_in_polder(message.guild, content=content, message_id=message.id, author_id=message.author.id, channel_id=message.channel.id)

    @commands.command(name="enablerandomtextposts", aliases=['erandomtext'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def enable_random_text_posts(self, ctx):
        """[Default Admin command] Enables random text posting. Use this if you want polder to post randomly generated text."""
        params = await self.bot.servers.get_server_parameters(ctx.guild, "random_text_posts")
        if params.get("random_text_posts"):
            await ctx.reply("Random text posting is already enabled.")
            return
        params.update({"random_text_posts":True})
        await self.bot.servers.update_server_parameters(ctx.guild, **params)
        await ctx.reply("Random text posting is now enabled.")

    @commands.command(name="disablerandomtextposts", aliases=['drandomtext'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def disable_random_text_posts(self, ctx):
        """[Default Admin command] Disables random text posting. Use this if you don't want polder to post randomly generated text."""
        params = await self.bot.servers.get_server_parameters(ctx.guild, "random_text_posts")
        if not params.get("random_text_posts"):
            await ctx.reply("Random text posting is already disabled.")
            return
        params.update({"random_text_posts":False})
        await self.bot.servers.update_server_parameters(ctx.guild, **params)
        await ctx.reply("Random text posting is now disabled.")

    @commands.command(name="enablerandompolderposts", aliases=['erandompolder'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def enable_random_polder_posts(self, ctx):
        """[Default Admin command] Enables random polder posting. Use this if you want PolBot to post things from polder."""
        params = await self.bot.servers.get_server_parameters(ctx.guild, "random_polder_posts")
        if params.get("random_polder_posts"):
            await ctx.reply("Random polder posting is already enabled.")
            return
        params.update({"random_polder_posts":True})
        await self.bot.servers.update_server_parameters(ctx.guild, **params)
        await ctx.reply("Random polder posting is now enabled.")

    @commands.command(name="disablerandompolderposts", aliases=['drandompolder'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def disable_random_polder_posts(self, ctx):
        """[Default Admin command] Disables random polder posting. Use this if you want PolBot to stop posting things from polder, for whatever reason."""
        params = await self.bot.servers.get_server_parameters(ctx.guild, "random_polder_posts")
        if not params.get("random_polder_posts"):
            await ctx.reply("Random polder posting is already disabled.")
            return
        params.update({"random_polder_posts":False})
        await self.bot.servers.update_server_parameters(ctx.guild, **params)
        await ctx.reply("Random polder posting is now disabled.")

    async def _post_random_polder(self, message:discord.Message, params):
        """Finds a random thing in polder and posts it."""
        if params.get("random_polder_posts"):
            content = await self.bot.servers.get_random_polder(message.guild)
            if content is not None:
                message_id, channel_id = content
                channel = discord.utils.get(message.guild.channels, id=channel_id)
                if channel is not None:
                    try:
                        polder_message = await channel.fetch_message(message_id)
                    except discord.NotFound:
                        await self.bot.servers.remove_in_polder(message.guild, message_id=message_id)
                        return await self._post_random_polder(message, params) #recursively try again
                    except discord.Forbidden:
                        message.channel.send("Error: I am unable to access polder messages due to permissions.")
                        return
                    except discord.HTTPException:
                        return
                    await message.channel.send(polder_message.content, allowed_mentions=mute_all_pings)

    async def _post_random_text(self, message:discord.Message, params):
        """Make random text. Default params: scrape 1000 messages, weight 100:1 chat to theory, try 100 times"""
        if params.get("random_text_posts"):
            if self.bot.making_text:
                await message.channel.send(content="Currently generating text, please try again later", delete_after=5)
                return
            self.bot.making_text = True
            async with message.channel.typing():
                text = await self._scrape_text(message.channel, limit=1000)
                chatchain = markovify.NewlineText(text)
                async with aiofiles.open((Path("corpi") / "politicalchain.json").resolve(), "r") as f:
                    text = await f.read()
                polchain = markovify.NewlineText.from_json(text)
                netchain = markovify.combine([polchain, chatchain], [1, 100])
                await message.channel.send(content=netchain.make_sentence(tries=100))
            self.bot.making_text = False

    async def _post_listener(self, message, params, method):
        """Runs a shitposting method if the probability chance is met"""
        if random()*100 < params.get("shitpost_probability"):
            await method(message, params)

    @commands.command(name="allowshitpostinghere",aliases=['eshitposting'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def allow_shitposting_here(self, ctx):
        """[Default Admin command] Enables shitposting in the current channel. When this is run, PolBot adds this to a list of allowed channels where he can shitpost."""
        if await self.bot.servers.add_in_shitposting_channels(ctx.guild, ctx.channel.id):
            await ctx.reply("I will shitpost here :^)")
            return
        await ctx.reply("I can already shitpost here you twat")

    @commands.command(name="disallowshitpostinghere",aliases=['dshitposting'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def disallow_shitposting_here(self, ctx):
        """[Default Admin command] Disables shitposting in the current channel. When this is run, PolBot removes this from a list of allowed channels where he can shitpost."""
        if await self.bot.servers.remove_in_shitposting_channels(ctx.guild, ctx.channel.id):
            await ctx.reply("I will not shitpost here :^(")
            return
        await ctx.reply("You already prevented me from shitposting here, you twat")

    @commands.command(name="setshitpostingprobability", aliases=['setpostprob'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def set_shitposting_probability(self, ctx, percentage):
        """[Default Admin command] Sets the probability that PolBot will randomly post something. Percentage must be a decimal between 0 and 100."""
        try:
            shitpost_probability = float(percentage)
        except ValueError:
            await ctx.reply(f"{percentage} is not a valid decimal number between 0 and 100.")
            return
        params = await self.bot.servers.get_server_parameters(ctx.guild, "shitpost_probability")
        params.update({"shitpost_probability":shitpost_probability})
        await self.bot.servers.update_server_parameters(ctx.guild, **params)
        await ctx.reply(f'Set the shitposting probability to {shitpost_probability}%')
    
    @commands.command(name="getshitpostingprobability", aliases=['postprob?'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def get_shitposting_probability(self, ctx):
        """[Default Mod command] Gets the probability that PolBot will randomly post something."""
        params = await self.bot.servers.get_server_parameters(ctx.guild, "shitpost_probability")
        await ctx.reply(f"I have a {params.get('shitpost_probability')}% chance to shitpost after a message is posted in my allowed channels")

    def _strip_trailing_by_punc(self, text:str):
        punctuation_positions = [text.find(punc) for punc in punctuation]
        negatives_removed = list(filter(lambda x: x != -1, punctuation_positions))
        if len(negatives_removed) == 0:
            return text
        else:
            return text[:min(negatives_removed)]
    
    @commands.command(name="say")
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def say(self, ctx, channel:discord.TextChannel, *, flags: utils.SayFlags):
        """
        Speak through the bot.
        channel: Required; the channel to speak in. Can be a # reference or an ID
        -text: Required; the text to say.
        -replyto: Optional; the message to reply to. Usually specified by ID.
        """
        await channel.send(" ".join(flags.text), allowed_mentions=mute_role_and_everyone_pings, reference=flags.replyto)

    @commands.command(name="react")
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def say(self, ctx, channel:discord.TextChannel, *, flags: utils.ReactFlags):
        """
        React to messages with the bot.
        channel: Required; the channel to react in. Can be a # reference or an ID
        -message: Required; the message to react to.
        -reactions: Required; the reaction(s) to apply to the specified message. This can be multiple, or just one.
        """
        reactions = [self._react(flags.message, reaction) for reaction in flags.reactions]
        await asyncio.gather(*reactions)

    @commands.command(name="markov", aliases=['m'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    @commands.check(cogs.permissionshandler.markov_command_running)
    async def markov(self, ctx, flags:utils.MarkovFlags):
        """Produce random text produced from political theory and the chat. This is a beta feature.
        
        valid flags:
        -tries: Optional; number of times to attempt to start a chain. Default 100 if unspecified.
        -limit: Optional; number of messages to read in the current channel, starting from the current message. Default 5000 if unspecified.
        -cweight: Optional; how much weight to attribute to the chat messages. Default 100 if unspecified.
        -dweight: Optional; how much weight to attribute to the political theory. Default 1 if unspecified.
        """
        async with ctx.channel.typing():
            self.bot.making_text = True
            text = await self._scrape_text(ctx.channel, limit=flags.limit)
            chatchain = markovify.NewlineText(text)
            async with aiofiles.open((Path("corpi") / "politicalchain.json").resolve(), "r") as f:
                text = await f.read()
            polchain = markovify.NewlineText.from_json(text)
            netchain = markovify.combine([polchain, chatchain], [flags.dweight, flags.cweight])
            if flags.dump is not None:
                await flags.dump.send(content=(netchain.make_sentence(tries=flags.tries) or "Failed to generate a sentence"))
                return
            else:
                await ctx.send(content=(netchain.make_sentence(tries=flags.tries) or "Failed to generate a sentence"))
        self.bot.making_text = False

    async def _scrape_text(self, channel, **kwargs):
        """Make a corpus from chat of text suitable for a chain"""
        valid_params = ["limit"] # allowed keywords
        params = {k : v for k, v in kwargs.items() if k in valid_params and v is not None} # sanitizes kwargs
        return "\n".join([message.content async for message in channel.history(limit=params.get("limit")) if (re.match(self.RE_MESSAGE_MATCH, message.content) and not message.author.bot)])
    
    @commands.command(name='makecorpus', aliases=['mc'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.owner_check)
    async def initialize_corpus(self, ctx):
        """Initializes the political theory corpus and saves to JSON."""
        await ctx.channel.send(content="Initializing corpus")
        async with ctx.channel.typing():
            chains=[]
            for _, _, filenames in walk(Path("corpi")):
                for filename in filenames:
                    async with aiofiles.open((Path("corpi") / filename).resolve(), "r") as f:
                        text = await f.read()
                    chains.append(markovify.NewlineText(text))
            pol_chain = markovify.combine(chains)
            text = pol_chain.to_json()
            async with aiofiles.open((Path("corpi") / "politicalchain.json").resolve(), "w") as f:
                await f.write(text)
        await ctx.channel.send(content="Finished initializing corpus")
    
    async def _react(self, message: discord.Message, reaction:utils.Emoji):
        await message.add_reaction(reaction)