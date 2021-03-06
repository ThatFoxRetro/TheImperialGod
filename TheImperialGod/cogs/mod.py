import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.ext.commands import MissingPermissions, BadArgument
from asyncio import sleep
from discord.ext.commands import cooldown, BucketType
import random
import json

class Mod(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Mod commands Loaded!")

    @commands.command(aliases = ["purge", "massdelete", "bulkdel"])
    @has_permissions(manage_messages = True)
    async def clear(self, ctx, amount = 1):
        await ctx.channel.purge(limit = amount)
        
    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            embed = discord.Embed(title = "<:fail:761292267360485378> Purge Failed!", color = ctx.author.color)
            embed.add_field(name = "Reason:", value = f"`Manage Messages Permissions Missing!`")
            await ctx.send(embed = embed)

    @commands.command()
    @has_permissions(manage_channels = True)
    async def lock(self, ctx, *, reason = None):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages = False, read_messages = True)
        em = discord.Embed(title = f"<:success:761297849475399710> Channel has been locked!", color = discord.Color.green())
        em.add_field(name = "**Responsible Moderator:**", value = f"`{ctx.author.name}`")
        em.add_field(name = "**Reason:**", value = f"`{reason}`")
        em.add_field(name=  "Description", value = "You are not muted this channel is locked! No one but mods can type in this channel!", inline = False)
        await ctx.channel.send(embed = em)    
        
    @lock.error
    async def lock_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            embed = discord.Embed(title = "<:fail:761292267360485378> Lock Failed!", color = ctx.author.color)
            embed.add_field(name = "Reason:", value = f"Manage Channels Permissions Missing!")
            await ctx.send(embed = embed)

    @commands.command()
    @has_permissions(manage_channels = True)
    async def unlock(self, ctx, *, reason = None):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages = True, read_messages = True)
        em = discord.Embed(title = f"<:success:761297849475399710> Channel has been unlocked!", color = discord.Color.green())
        em.add_field(name = "**Responsible Moderator:**", value = f"`{ctx.author.name}`")
        em.add_field(name = "**Reason:**", value = f"`{reason}`")
        em.add_field(name=  "Description", value = "You are not unmuted this channel is unlocked! No one but mods can type in this channel!", inline = False)
        await ctx.channel.send(embed = em)    

    @unlock.error
    async def unlock_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            embed = discord.Embed(title = "<:fail:761292267360485378> Unlock Failed!", color = ctx.author.color)
            embed.add_field(name = "Reason:", value = f"Manage Channels Permissions Missing!")
            await ctx.send(embed = embed)

    @commands.command()
    @has_permissions(manage_channels = True)
    async def setdelay(self, ctx, amount = 5, *, reason = None):
        if amount > 6000:
            await ctx.channel.send("Amount needs to be less than 6000!")
            return

        await ctx.channel.edit(slowmode_delay=amount)
        em = discord.Embed(title = "<:success:761297849475399710> Change in channel settings", color = ctx.author.color)
        em.add_field(name = "**Responsible Moderator:**", value = f"`{ctx.author.name}`")
        em.add_field(name = "**Reason:**", value = f"`{reason}`")
        em.add_field(name=  "Description", value = f"Now the channel has a slowmode which avoids spamming\n {ctx.author.mention} for more type `imp lock [reason]`", inline = False)
        em.add_field(name = "Slowmode", value = f"`{amount} seconds`")
        await ctx.send(embed = em)

    @setdelay.error
    async def setdelay_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            embed = discord.Embed(title = "Setdelay Failed!", color = ctx.author.color)
            embed.add_field(name = "Reason:", value = f"Manage Channels Permissions Missing!")
            await ctx.send(embed = embed)

    @commands.command()
    @has_permissions(ban_members = True)
    async def unban(ctx, member : str, *, reason = None):
        banned_users = await ctx.guild.bans()
        member_name, member_disc = member.split("#")

        for banned_entry in banned_users:
            user = banned_entry.user

            if (user.name, user.discriminator) == (member_name, member_disc):
                await ctx.guild.unban(user)
                embed = discord.Embed(title = f"{member_name} was unbanned!", color = ctx.author.color)
                embed.add_field(name = "Reason:", value = f"`{reason}`")
                embed.add_field(name = "Moderator:", value = f"`{ctx.author.name}`")
                await ctx.send(embed = embed)
                return

        await ctx.send("Not a valid user, try it like this:\n`imp unban name#disc`")

    #normal function
    def convert(self, time):
        pos = ["s","m","h","d"]

        time_dict = {"s" : 1, "m" : 60, "h" : 3600 , "d" : 3600*24}

        unit = time[-1]

        if unit not in pos:
            return -1
        try:
            val = int(time[:-1])
        except:
            return -2

        return val * time_dict[unit]

    @commands.command()
    @has_permissions(manage_channels = True)
    async def count(ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel #or since sometimes people have it locked!
        messages = await channel.history(limit = None).flatten()
        count = len(messages)

        embed = discord.Embed(
        title="Total Messages",
        colour=ctx.author.color,
        description=f"There were {count} messages in {channel.mention}")

        await ctx.send(embed=embed)

    @commands.command()
    @has_permissions(kick_members = True)
    async def kick(self, ctx, member : discord.Member = None, *, reason = None):
        if member == None:
            embed = discord.Embed(title = "<:fail:761292267360485378> Kick Failed!", color= ctx.author.color)
            embed.add_field(name = "Reason:", value = "Ping a user to kick them!")
            await ctx.send(embed = embed)
        await member.kick(reason = reason)
        em = discord.Embed(title = f"<:success:761297849475399710> Kick was successful!", color = ctx.author.color)
        em.add_field(name = f"Victim:", value = f"`{member.name}`")
        em.add_field(name = "Reason: ", value = f"`{reason}`")
        em.add_field(name = "Moderator:", value = f"`{ctx.author.name}`")
        await ctx.send(embed = em)
        try:
            await member.send(f"You were kicked in {ctx.guild.name}\nReason: `{reason}`\nModerator: `{ctx.author.name}`")
        except:
            pass

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            em = discord.Embed(title = "<:fail:761292267360485378> Kick Failed!", color = ctx.author.color)
            em.add_field(name = "Reason:", value = "`Kick members Permission Missing!`")
            await ctx.send(embed = em)
        if isinstance(error, commands.BadArgument):
            em = discord.Embed(title = "<:fail:761292267360485378> Kick Failed!", color = ctx.author.color)
            em.add_field(name = "Reason:", value = "`Ping a user to kick them!`")
            await ctx.send(embed = em)

    @commands.command()
    @has_permissions(ban_members = True)
    async def ban(self, ctx, member : discord.Member = None, *,reason = None):
        if member == None:
            embed = discord.Embed(title = "<:fail:761292267360485378> Ban Failed!", color= ctx.author.color)
            embed.add_field(name = "Reason:", value = "Ping a user to ban them!")
            await ctx.send(embed = embed)
        await member.ban(reason = reason)
        em = discord.Embed(title = f"<:success:761297849475399710> Ban was successful!", color = ctx.author.color)
        em.add_field(name = f"Victim:", value = f"`{member.name}`")
        em.add_field(name = "Reason: ", value = f"`{reason}`")
        em.add_field(name = "**Moderator**:", value = f"`{ctx.author.name}`")
        await ctx.send(embed = em)
        try:
            await member.send(f"You were banned in {ctx.guild.name}\nReason: `{reason}`\nModerator: `{ctx.author.name}`")
        except:
            pass
    
    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            em = discord.Embed(title = "<:fail:761292267360485378> Ban Failed!", color = ctx.author.color)
            em.add_field(name = "Reason:", value = "`Ban members Permission Missing!`")
            await ctx.send(embed = em)
        if isinstance(error, commands.BadArgument):
            em = discord.Embed(title = "<:fail:761292267360485378> Ban Failed!", color = ctx.author.color)
            em.add_field(name = "Reason:", value = "`Ping a user to Ban them!`")
            await ctx.send(embed = em)
    
    @commands.command()
    @has_permissions(administrator = True)
    async def enableautomod(self, ctx, *, reason = None):
        with open("./data/automod.json", "r") as f:
            guilds = json.load(f)
        
        with open("./data/emojis.json", "r") as f:
            emojis = json.load(f)

        if str(ctx.guild.id) in guilds:
            guilds[str(ctx.guild.id)]["automod"] = "true"
        else:
            guilds[str(ctx.guild.id)] = {}
            guilds[str(ctx.guild.id)]["automod"] = "true"

        embed = discord.Embed(title = f"<:success:761297849475399710> change in server settings!", color = ctx.author.color,
        description = "An awesome moderator, enabled automod. Beware no more **bad words!**"
        )
        embed.add_field(name = "Automod Status:", value = f"`Automod = True`")
        embed.add_field(name = "Reason:", value = f"`{reason}`")
        embed.add_field(name = "Moderator:", value = f"`{ctx.author.name}`", inline = False)
        await ctx.send(embed = embed)

        with open("./data/automod.json", "w") as f:
            json.dump(guilds, f)

    @enableautomod.error
    async def enableautomod_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Bruh you really think you can use that?")
    
    @commands.command()
    @has_permissions(administrator = True)
    async def disableautomod(self, ctx, *, reason = None):
        with open("./data/automod.json", "r") as f:
            guilds = json.load(f)

        with open("./data/emojis.json","r") as f:
            emojis = json.load(f)

        if str(ctx.guild.id) in guilds:
            guilds[str(ctx.guild.id)]["automod"] = "false"
        else:
            guilds[str(ctx.guild.id)] = {}
            guilds[str(ctx.guild.id)]["automod"] = "false"

        embed = discord.Embed(title = f'<:success:761297849475399710> Change in Server Settings', color = ctx.author.color)
        embed.add_field(name = 'Automod:', value = "`Automod = False`")
        embed.add_field(name = "Reason:", value = f"`{reason}`")
        embed.add_field(name = "Moderator:", value = f"`{ctx.author.name}`", inline = False)
        await ctx.send(embed = embed)

        with open("./data/automod.json", "w") as f:
            json.dump(guilds, f)

    @disableautomod.error
    async def disableautomod_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Bruh you really think you can use that?")

    @commands.command()
    async def checkautomod(self,ctx):
        with open("./data/automod.json", "r") as f:
            guilds = json.load(f)
        
        embed = discord.Embed(title = f"Automoderation status of {ctx.guild.name}", color = ctx.author.color)

        if str(ctx.guild.id) in guilds:
            if guilds[str(ctx.guild.id)]["automod"] == "true":
                embed.add_field(name = "Automod Status:", value = f"`True`")
            elif guilds[str(ctx.guild.id)]["automod"] == "false":
                embed.add_field(name = "Automod Status:", value = f"`False`")
            await ctx.send(embed = embed)
        else:
            embed.add_field(name = "Automod Status:", value = f"`<:fail:761292267360485378> Not set up!`")
            embed.add_field(name = "What to do?", value = "Ask a mod to set this up!")
            await ctx.send(embed = embed)

    @commands.command()
    @commands.has_permissions(manage_channels = True)
    async def announce(ctx, channel : discord.TextChannel, *, msg):
        embed = discord.Embed(title = "Announcement!", color = ctx.author.color)
        embed.add_field(name = "Announcement:", value = f"`{msg}`")
        embed.add_field(name = "Moderator:", value = f"`{ctx.autor.name}`")
        await channel.send(embed = embed)

    @announce.error
    async def announce_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title = "Announcement failed!", color = ctx.author.color)
            embed.add_field(name = 'Reason:', value = "Some perms are missing")
            await ctx.send(embed = embed)
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(title = "Announcement failed!", color = ctx.author.color)
            embed.add_field(name = 'Reason:', value = f"Mention a channel properly! And write a message after it!")
            await ctx.send(embed = embed)

def setup(client):
    client.add_cog(Mod(client))