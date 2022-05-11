import discord
import cogs.permissionshandler
from discord.ext import commands
from random import random, sample

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
            await self._post_listener(message, params, self._post_random_image)
            await self._post_listener(message, params, self._post_random_text)
        await self._add_polder_post(message, params)

    @commands.command(name="setpolderhere", aliases=['setpolder'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def set_polder_here(self, ctx):
        """Sets the polder channel to the current channel. All images posted in the polder channel will be randomly posted as images in the allowed channels."""
        params = self.bot.servers.get_server_parameters(ctx.guild)
        params.update({"polder_channel_id":ctx.channel.id})
        self.bot.servers.update_server_parameters(ctx.guild, params)
        await ctx.reply(f"Set the polder channel to #{ctx.channel.name}")

    @commands.command(name="enablepolder", aliases=['epolder'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def enable_polder(self, ctx):
        """Enables polder image collection."""
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
        """Disables polder image collection."""
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
        """When this command is run in a reply to an image posted by PolBot, it removes the image from polbot's available images to post."""
        posted_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        if posted_message.author.id != self.bot.user.id:
            await ctx.reply("The message you replied to is not something *I* posted, you twat.")
            return
        # IMPORTANT: Assumes that PolBot can only post 1 image per image shitpost
        discord_media_link = posted_message.attachments.pop(0).url
        if self.bot.servers.remove_in_polder(ctx.guild, discord_media_link):
            await ctx.reply("I won't post *that* ever again ;)")
            return
        await ctx.reply("I don't remember having *that* saved (I may be having a stroke, please call my master)")


    async def _add_polder_post(self, message:discord.Message, params):
        """Adds an image link to PolBot's repetoire."""
        if message.channel.id == params.get("polder_channel_id") and params.get("polder_enabled"):
            # IMPORTANT: Assumes that PolBot can only post 1 image per image shitpost. Multiple images won't be added
            try:
                image = message.attachments.pop(0)
                self.bot.servers.add_in_polder(message.guild, image.url, message)
            except IndexError:
                return
    

    @commands.command(name="enablerandomtextposts", aliases=['erandomtext'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def enable_random_text_posts(self, ctx):
        """Enables random text posting."""
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
        """Disables random text posting."""
        params = self.bot.servers.get_server_parameters(ctx.guild)
        if not params.get("random_text_posts_enabled"):
            await ctx.reply("Random text posting is already disabled.")
            return
        params.update({"random_image_posts_enabled":False})
        self.bot.servers.update_server_parameters(ctx.guild, params)
        await ctx.reply("Random image posting is now disabled.")

    @commands.command(name="enablerandomimageposts", aliases=['erandomimage'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def enable_random_image_posts(self, ctx):
        """Enables random image posting."""
        params = self.bot.servers.get_server_parameters(ctx.guild)
        if params.get("random_image_posts_enabled"):
            await ctx.reply("Random image posting is already enabled.")
            return
        params.update({"random_image_posts_enabled":True})
        self.bot.servers.update_server_parameters(ctx.guild, params)
        await ctx.reply("Random image posting is now enabled.")

    @commands.command(name="disablerandomimageposts", aliases=['drandomimage'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def disable_random_image_posts(self, ctx):
        """Disables random image posting."""
        params = self.bot.servers.get_server_parameters(ctx.guild)
        if not params.get("random_image_posts_enabled"):
            await ctx.reply("Random text posting is already disabled.")
            return
        params.update({"random_image_posts_enabled":False})
        self.bot.servers.update_server_parameters(ctx.guild, params)
        await ctx.reply("Random image posting is now disabled.")

    async def _post_random_image(self, message:discord.Message, params):
        """Finds a random image in polder and posts it."""
        if params.get("random_image_posts_enabled"):
            await message.channel.send(self.bot.servers.get_random_polder(message.guild))
    
    async def _post_random_text(self, message:discord.Message, params):
        if params.get("random_text_posts_enabled"):
            messages = [message.content async for message in message.channel.history(limit=50)]
            words = ' '.join(messages).split()
            shitpost = sample(words, int(random()*len(words)/2)) #Restricts the sample of words to be at most half the length of words
            shitpost = " ".join(shitpost)
            shitpost = discord.utils.escape_mentions(shitpost) #ALHAMDULILAH
            await message.channel.send(shitpost[:2000])
    
    async def _post_listener(self, message, params, method):
        """Controls the probability chance of a shitpost occurring."""
        if random()*100 < params.get("shitpost_probability"):
            await method(message, params)

    @commands.command(name="allowshitpostinghere",aliases=['eshitposting'])
    @commands.check(cogs.permissionshandler.PermissionsHandler.admin_check)
    async def allow_shitposting_here(self, ctx):
        """Enables shitposting in the current channel."""
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
        """Disables shitposting in the current channel."""
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
        """Sets the probability that I will randomly post a text or meme. Percentage must be a decimal between 0 and 100."""
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
        """Gets the probability that I will randomly post a text or meme."""
        params = self.bot.servers.get_server_parameters(ctx.guild)
        await ctx.reply(f"I have a {params.get('shitpost_probability')}% chance to shitpost after a message is posted in my allowed channels")