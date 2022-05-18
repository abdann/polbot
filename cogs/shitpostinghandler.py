import discord
import cogs.permissionshandler
from discord.ext import commands
from random import random, sample
import re

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
        params = self.bot.servers.get_server_parameters(message.guild)
        if message.channel.id in params.get("shitposting_channels"):
            await self._post_listener(message, params, self._post_random_polder)
            await self._post_listener(message, params, self._post_random_text)
        await self._add_polder_post(message, params)

    @commands.command(name="setpolderhere", aliases=['setpolder'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def set_polder_here(self, ctx):
        """[Admin command] Sets the polder channel to the current channel. All images and text posted in the polder channel will have a chance to be randomly posted in the allowed channels. This is separate from the randomly generated text posting."""
        params = self.bot.servers.get_server_parameters(ctx.guild)
        params.update({"polder_channel_id":ctx.channel.id})
        self.bot.servers.update_server_parameters(ctx.guild, params)
        await ctx.reply(f"Set the polder channel to #{ctx.channel.name}")

    @commands.command(name="enablepolder", aliases=['epolder'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def enable_polder(self, ctx):
        """[Admin command] Enables polder image collection. Use this if you want PolBot to save text and images from polder."""
        params = self.bot.servers.get_server_parameters(ctx.guild)
        if params.get("polder_enabled"):
            await ctx.reply("Polder image collection is already enabled.")
            return
        params.update({"polder_enabled":True})
        self.bot.servers.update_server_parameters(ctx.guild, params)
        await ctx.reply("Polder image collection is now enabled.")

    @commands.command(name="disablepolder", aliases=['dpolder'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def disable_polder(self, ctx):
        """[Admin command] Disables polder content collection. Use this if you want to prevent PolBot from saving text and images from polder, for whatever reason."""
        params = self.bot.servers.get_server_parameters(ctx.guild)
        if not params.get("polder_enabled"):
            await ctx.reply("Polder image collection is already disabled.")
            return
        params.update({"polder_enabled":False})
        self.bot.servers.update_server_parameters(ctx.guild, params)
        await ctx.reply("Polder image collection is now disabled.")

    @commands.command(name="removepolderpost", aliases=['rmpolderpost'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def remove_polder_post(self, ctx):
        """[Moderator command] When this command is run in a reply to a polder post posted by PolBot, it removes the polder post from PolBot's memory."""
        posted_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        params = self.bot.servers.get_server_parameters(ctx.guild)
        if ctx.channel.id == params.get("polder_channel_id"):
        # if posted_message.author.id != self.bot.user.id:
        #     await ctx.reply("The message you replied to is not something *I* posted, you twat.")
        #     return
            if len(posted_message.attachments) != 0: #For image posts from polder
                # IMPORTANT: Assumes that PolBot can only post 1 image per image shitpost
                discord_media_link = posted_message.attachments.pop(0).url
                if self.bot.servers.remove_in_polder(ctx.guild, discord_media_link):
                    # await ctx.reply("I won't post *that* ever again ;)")
                    await ctx.reply("I didn't see nuffin' ;)")
                    return
                await ctx.reply("I don't remember having *that* saved (I may be having a stroke, please call my master)")
            else: # For text posts from polder
                if self.bot.servers.remove_in_polder(ctx.guild, posted_message.content):
                    await ctx.reply("I didn't see nuffin' ;)")
                    return
                await ctx.reply("I don't remember having *that* saved (I may be having a stroke, please call my master)")
        else: #Assumes that we are anywhere else other than polder
            if posted_message.author.id != self.bot.user.id:
                await ctx.reply("The message you replied to is not something *I* posted, you twat.")
                return
            else: # Implies that PolBot posted posted_message
                if len(posted_message.attachments) != 0: #For image posts from polder
                    # IMPORTANT: Assumes that PolBot can only post 1 image per image shitpost
                    discord_media_link = posted_message.attachments.pop(0).url
                    if self.bot.servers.remove_in_polder(ctx.guild, discord_media_link):
                        await ctx.reply("I won't post *that* ever again ;)")
                        return
                    await ctx.reply("I don't remember having *that* saved (I may be having a stroke, please call my master)")
                else: # For text posts from polder
                    if self.bot.servers.remove_in_polder(ctx.guild, posted_message.content):
                        await ctx.reply("I won't post *that* ever again ;)")
                        return
                    await ctx.reply("I don't remember having *that* saved (I may be having a stroke, please call my master)")



    async def _add_polder_post(self, message:discord.Message, params):
        """Adds an image link OR message text to PolBot's repetoire of things he can post from polder."""
        if message.channel.id == params.get("polder_channel_id") and params.get("polder_enabled"):
            # IMPORTANT: Assumes that PolBot can only post 1 image per image shitpost. Multiple images won't be added. Also assumes that an image is posted separately from text
            if len(message.attachments) != 0:
                image = message.attachments.pop(0)
                self.bot.servers.add_in_polder(message.guild, image.url, message)
            else:
                self.bot.servers.add_in_polder(message.guild, message.content, message)
    

    @commands.command(name="enablerandomtextposts", aliases=['erandomtext'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def enable_random_text_posts(self, ctx):
        """[Admin command] Enables random text posting. Use this if you want polder to post randomly generated text."""
        params = self.bot.servers.get_server_parameters(ctx.guild)
        if params.get("random_text_posts_enabled"):
            await ctx.reply("Random text posting is already enabled.")
            return
        params.update({"random_text_posts_enabled":True})
        self.bot.servers.update_server_parameters(ctx.guild, params)
        await ctx.reply("Random text posting is now enabled.")

    @commands.command(name="disablerandomtextposts", aliases=['drandomtext'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def disable_random_text_posts(self, ctx):
        """[Admin command] Disables random text posting. Use this if you don't want polder to post randomly generated text."""
        params = self.bot.servers.get_server_parameters(ctx.guild)
        if not params.get("random_text_posts_enabled"):
            await ctx.reply("Random text posting is already disabled.")
            return
        params.update({"random_text_posts_enabled":False})
        self.bot.servers.update_server_parameters(ctx.guild, params)
        await ctx.reply("Random text posting is now disabled.")

    @commands.command(name="enablerandompolderposts", aliases=['erandompolder'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def enable_random_polder_posts(self, ctx):
        """[Admin command] Enables random polder posting. Use this if you want PolBot to post things from polder."""
        params = self.bot.servers.get_server_parameters(ctx.guild)
        if params.get("random_polder_posts_enabled"):
            await ctx.reply("Random polder posting is already enabled.")
            return
        params.update({"random_polder_posts_enabled":True})
        self.bot.servers.update_server_parameters(ctx.guild, params)
        await ctx.reply("Random polder posting is now enabled.")

    @commands.command(name="disablerandompolderposts", aliases=['drandompolder'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def disable_random_polder_posts(self, ctx):
        """[Admin command] Disables random polder posting. Use this if you want PolBot to stop posting things from polder, for whatever reason."""
        params = self.bot.servers.get_server_parameters(ctx.guild)
        if not params.get("random_polder_posts_enabled"):
            await ctx.reply("Random polder posting is already disabled.")
            return
        params.update({"random_polder_posts_enabled":False})
        self.bot.servers.update_server_parameters(ctx.guild, params)
        await ctx.reply("Random polder posting is now disabled.")

    async def _post_random_polder(self, message:discord.Message, params):
        """Finds a random thing in polder and posts it."""
        if params.get("random_polder_posts_enabled"):
            await message.channel.send(discord.utils.escape_mentions(self.bot.servers.get_random_polder(message.guild)))
    
    async def _post_random_text(self, message:discord.Message, params):
        """Creates a random piece of text from the 20 previous messages in chat. Filters links and mentions, and limits the output to 2000 characters (discord limit)"""
        if params.get("random_text_posts_enabled"):
            messages = [message.content async for message in message.channel.history(limit=20)] #Get list of 20 most recent message contents
            words_as_string = ' '.join(messages) # Separate into list of words
            words = re.sub(r'http\S+', '', words_as_string) #filter out links
            words = words.split()
            shitpost = sample(words, int(random()*len(words)/2)) #Restricts the sample of words to be at most half the length of words
            shitpost = " ".join(shitpost) # combine them into a single string
            shitpost = discord.utils.escape_mentions(shitpost) #ALHAMDULILAH
            await message.channel.send(shitpost[:2000]) #limits to 2000 characters (discord limit)
    
    async def _post_listener(self, message, params, method):
        """Runs a shitposting method if the probability chance is met"""
        if random()*100 < params.get("shitpost_probability"):
            await method(message, params)

    @commands.command(name="allowshitpostinghere",aliases=['eshitposting'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def allow_shitposting_here(self, ctx):
        """[Admin command] Enables shitposting in the current channel. When this is run, PolBot adds this to a list of allowed channels where he can shitpost."""
        params = self.bot.servers.get_server_parameters(ctx.guild)
        if ctx.channel.id in params.get("shitposting_channels"):
            await ctx.reply("I can already shitpost here you twat")
            return
        params.get("shitposting_channels").append(ctx.channel.id)
        self.bot.servers.update_server_parameters(ctx.guild, params)
        await ctx.reply("I will shitpost here :^)")

    @commands.command(name="disallowshitpostinghere",aliases=['dshitposting'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def disallow_shitposting_here(self, ctx):
        """[Admin command] Disables shitposting in the current channel. When this is run, PolBot removes this from a list of allowed channels where he can shitpost."""
        params = self.bot.servers.get_server_parameters(ctx.guild)
        if not ctx.channel.id in params.get("shitposting_channels"):
            await ctx.reply("You already prevented me from shitposting here, you twat")
            return
        params.get("shitposting_channels").remove(ctx.channel.id)
        self.bot.servers.update_server_parameters(ctx.guild, params)
        await ctx.reply("I will not shitpost here :^(")

    @commands.command(name="setshitpostingprobability", aliases=['setpostprob'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def set_shitposting_probability(self, ctx, percentage):
        """[Admin command] Sets the probability that PolBot will randomly post something. Percentage must be a decimal between 0 and 100."""
        try:
            shitpost_probability = float(percentage)
        except ValueError:
            await ctx.reply(f"{percentage} is not a valid decimal number between 0 and 100.")
            return
        params = self.bot.servers.get_server_parameters(ctx.guild)
        params.update({"shitpost_probability":shitpost_probability})
        self.bot.servers.update_server_parameters(ctx.guild, params)
        await ctx.reply(f'Set the shitposting probability to {shitpost_probability}%')
    
    @commands.command(name="getshitpostingprobability", aliases=['postprob?'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.moderator_check)
    async def get_shitposting_probability(self, ctx):
        """[Moderator command] Gets the probability that PolBot will randomly post something."""
        params = self.bot.servers.get_server_parameters(ctx.guild)
        await ctx.reply(f"I have a {params.get('shitpost_probability')}% chance to shitpost after a message is posted in my allowed channels")