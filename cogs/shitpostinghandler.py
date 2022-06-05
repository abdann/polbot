import discord
import cogs.permissionshandler
from discord.ext import commands
from random import random, sample
import re

no_ping = discord.AllowedMentions(everyone=False, users=False, roles=False, replied_user=False)
class ShitpostingHandler(commands.Cog, name='Shitposting'):
    """Handles all shitposting commands and features of the bot"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        if self.bot.user.mentioned_in(message):
            await message.reply("https://tenor.com/view/annoying-who-pinged-me-angry-gif-14512411")
        params = await self.bot.servers.get_server_parameters(message.guild, "a")
        if await self.bot.servers.find_in_shitposting_channels(message.guild, message.channel.id):
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

    # @commands.command(name="removepolderpost", aliases=['rmpolderpost'])
    # @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    # async def remove_polder_post(self, ctx):
    #     """[Default Mod command] When this command is run in a reply to a polder post posted by PolBot, it removes the polder post from PolBot's memory."""
    #     posted_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    #     params = await self.bot.servers.get_server_parameters(ctx.guild, "polder_channel_id")
    #     if ctx.channel.id == params.get("polder_channel_id"):
    #     # if posted_message.author.id != self.bot.user.id:
    #     #     await ctx.reply("The message you replied to is not something *I* posted, you twat.")
    #     #     return
    #         if len(posted_message.attachments) != 0: #For image posts from polder
    #             # IMPORTANT: Assumes that PolBot can only post 1 image per image shitpost
    #             discord_media_link = posted_message.attachments.pop(0).url
    #             if await self.bot.servers.remove_in_polder(ctx.guild, content=discord_media_link):
    #                 # await ctx.reply("I won't post *that* ever again ;)")
    #                 await ctx.reply("I didn't see nuffin' ;)")
    #                 return
    #             await ctx.reply("I don't remember having *that* saved (I may be having a stroke, please call my master)")
    #         else: # For text posts from polder
    #             if await self.bot.servers.remove_in_polder(ctx.guild, content=posted_message.content):
    #                 await ctx.reply("I didn't see nuffin' ;)")
    #                 return
    #             await ctx.reply("I don't remember having *that* saved (I may be having a stroke, please call my master)")
    #     else: #Assumes that we are anywhere else other than polder
    #         if posted_message.author.id != self.bot.user.id:
    #             await ctx.reply("The message you replied to is not something *I* posted, you twat.")
    #             return
    #         else: # Implies that PolBot posted posted_message
    #             if len(posted_message.attachments) != 0: #For image posts from polder
    #                 # IMPORTANT: Assumes that PolBot can only post 1 image per image shitpost
    #                 discord_media_link = posted_message.attachments.pop(0).url
    #                 if await self.bot.servers.remove_in_polder(ctx.guild, content=discord_media_link):
    #                     await ctx.reply("I won't post *that* ever again ;)")
    #                     return
    #                 await ctx.reply("I don't remember having *that* saved (I may be having a stroke, please call my master)")
    #             else: # For text posts from polder
    #                 if await self.bot.servers.remove_in_polder(ctx.guild, content=posted_message.content):
    #                     await ctx.reply("I won't post *that* ever again ;)")
    #                     return
    #                 await ctx.reply("I don't remember having *that* saved (I may be having a stroke, please call my master)")

    @commands.command(name="removepolderpost", aliases=['rmpolderpost'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def remove_polder_post(self, ctx):
        """[Default Mod command] When this command is run in a reply to a polder post posted by PolBot, it removes the polder post from PolBot's memory."""
        params = await self.bot.servers.get_server_parameters(ctx.guild, "polder_channel_id")
        posted_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        if ctx.channel.id == params.get("polder_channel_id"): #if we are in polder channel
            if posted_message.author.id != self.bot.user.id: #If the posted message to remove was not posted by the bot
                uploaded_media_link_list = [attachment.url for attachment in posted_message.attachments]
                uploaded_media_links = "\n".join(uploaded_media_link_list) if len(uploaded_media_link_list) > 0 else ""
                content = posted_message.content + "\n" + uploaded_media_links
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
    # async def _add_polder_post(self, message:discord.Message, params):
    #     """Adds an image link OR message text to PolBot's repetoire of things he can post from polder."""
    #     if message.channel.id == params.get("polder_channel_id") and params.get("polder"):
    #         if message.content.startswith(self.bot.command_prefix): # Exit if contains command
    #             return
    #         if message.author.id == self.bot.user.id: # Exit if bot message
    #             return
    #         # IMPORTANT: Assumes that PolBot can only post 1 image per image shitpost. Multiple images won't be added. Also assumes that an image is posted separately from text
    #         if len(message.attachments) != 0: #The post is a message
    #             image = message.attachments.pop(0)
    #             await self.bot.servers.add_in_polder(message.guild, content=image.url, message_id=message.id, author_id=message.author.id)
    #         else: #The post is a text
    #             await self.bot.servers.add_in_polder(message.guild, content=message.content, message_id=message.id, author_id=message.author.id)
    
    async def _add_polder_post(self, message:discord.Message, params):
        """Adds a message to PolBot's repetoire of things he can post from polder."""
        if message.channel.id == params.get("polder_channel_id") and params.get("polder"):
            if message.content.startswith(self.bot.command_prefix): # Exit if contains command
                return
            if message.author.id == self.bot.user.id: # Exit if bot message
                return
            uploaded_media_link_list = [attachment.url for attachment in message.attachments]
            uploaded_media_links = "\n".join(uploaded_media_link_list) if len(uploaded_media_link_list) > 0 else ""
            content = message.content + "\n" + uploaded_media_links
            await self.bot.servers.add_in_polder(message.guild, content=content, message_id=message.id, author_id=message.author.id)

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
                await message.channel.send(content, allowed_mentions=no_ping)
    
    async def _post_random_text(self, message:discord.Message, params):
        """Creates a random piece of text from the 20 previous messages in chat. Filters links and mentions, and limits the output to 2000 characters (discord limit)"""
        if params.get("random_text_posts"):
            messages = [message.content async for message in message.channel.history(limit=20)] #Get list of 20 most recent message contents
            words_as_string = ' '.join(messages) # Separate into list of words
            words = re.sub(r'http\S+', '', words_as_string) #filter out links
            words = words.split()
            shitpost = sample(words, int(random()*len(words)/2)) #Restricts the sample of words to be at most half the length of words
            shitpost = " ".join(shitpost) # combine them into a single string
            await message.channel.send(shitpost[:2000], allowed_mentions=no_ping) #limits to 2000 characters (discord limit)
    
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