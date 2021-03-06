from discord.ext import commands
import discord
import urllib.parse
import time
import math
import typing
import json
import asyncio
import utils.embed as qembed


class BeatSaber(commands.Cog,
                name='Beat Saber',
                command_attrs=dict(hidden=False)):
    '''Beat Saber Related Commands'''
    def __init__(self, bot):
        self.bot = bot
        self.bot.scoresaber = self.bot.data.scoresaber

    @staticmethod
    async def get_ss_stats(self, ctx, ssid):
        async with self.bot.session.get(
                f"https://new.scoresaber.com/api/player/{ssid}/full") as data:
            data = await data.json()
            grank = math.ceil(int(data['playerInfo']['rank']) / 50)
            crank = math.ceil(int(data['playerInfo']['countryRank']) / 50)
            embed = discord.Embed(
                title=f"{data['playerInfo']['playerName']}\'s Profile",
                url=f"https://new.scoresaber.com/u/{ssid}",
                description=
                f"**Player Ranking:** [#{data['playerInfo']['rank']}](https://new.scoresaber.com/rankings/{grank}) \n**Country Ranking:** {data['playerInfo']['country']} [#{data['playerInfo']['countryRank']}](https://scoresaber.com/global/{crank}&country={data['playerInfo']['country']}) \n**Performance Points:** {data['playerInfo']['pp']}pp"
            )
            embed.color = self.bot.embed_color
            embed.set_thumbnail(
                url=f"https://new.scoresaber.com{data['playerInfo']['avatar']}"
            )
            embed.add_field(
                name='Score Stats',
                value=
                f"**Play Count:** {data['scoreStats']['totalPlayCount']} \n**Ranked Play Count:** {data['scoreStats']['rankedPlayCount']} \n**Average Ranked Accuracy:** {data['scoreStats']['averageRankedAccuracy']:.2f}%",
                inline=False)
            embed.set_footer(text='Powered by the ScoreSaber API')
            await ctx.send(embed=embed)

    @staticmethod
    async def get_ssid(self, ctx, username):
        try:
            user = urllib.parse.quote_plus(username.upper())
            user = user.replace('+', '%20')
            async with self.bot.session.get(
                    f'https://new.scoresaber.com/api/players/by-name/{username}'
            ) as url:
                url = await url.json()
            return url['players'][0]['playerId']
        except:
            return url['error']['message']

    @commands.group(help='Collection of ScoreSaber commands')
    async def ss(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @ss.command(
        help=
        'Gets info about a user. This can be yourself or anyone on the Leaderboards',
        brief='Gets info about a user')
    async def info(self,
                   ctx,
                   *,
                   username: typing.Union[discord.Member, str] = None):
        async with ctx.typing():
            try:
                if isinstance(username, str):
                    ssid = await self.get_ssid(self, ctx, str(username))
                    await self.get_ss_stats(self, ctx, ssid)
                    return
            except KeyError:
                if len(username) < 3 or len(username) > 32:
                    await qembed.send(
                        ctx,
                        'Please enter a player name between 3 and 32 characters!'
                    )
                else:
                    await qembed.send(ctx, await
                                      self.get_ss_stats(self, ctx, ssid))
                return
            try:
                if isinstance(username, discord.Member):
                    if username in ctx.message.mentions:
                        data = await self.bot.scoresaber.find_one(
                            {"_id": username.id})
                        await self.get_ss_stats(self, ctx, data["ssid"])
                    else:
                        try:
                            u = username.display_name or username
                            await self.get_ss_stats(
                                self, ctx, await self.get_ssid(self, ctx, u))
                        except:
                            if len(username.display_name) < 3 or len(
                                    username.display_name) > 32:
                                await qembed.send(
                                    ctx,
                                    'Please enter a player name between 3 and 32 characters!'
                                )
                            else:
                                await qembed.send(
                                    ctx,
                                    'We could not find any players that matched your search!'
                                )
            except TypeError:
                await qembed.send(ctx, 'User is not registered!')
            if not username:
                try:
                    data = await self.bot.scoresaber.find_one(
                        {"_id": ctx.author.id})
                    await self.get_ss_stats(self, ctx, data["ssid"])
                except TypeError:
                    await qembed.send(
                        ctx,
                        f'You are not registered! Do `{ctx.prefix}help ss register` for info on how to register.'
                    )

    @ss.command(name='user', help='Ping a user and get their stats')
    async def u(self, ctx, person: discord.Member):
        try:
            with open('data.json', 'r') as f:
                data = json.load(f)
            message = await ctx.send(f'Getting stats for `{person.name}`')
            ssid = data['ssinfo'][str(person.id)]
            async with self.bot.session.get(
                    f"https://new.scoresaber.com/api/player/{ssid}/full"
            ) as data:
                data = await data.json()
                grank = math.ceil(int(data['playerInfo']['rank']) / 50)
                crank = math.ceil(int(data['playerInfo']['countryRank']) / 50)
                embed = discord.Embed(
                    title=f"{data['playerInfo']['playerName']}\'s Profile",
                    url=f"https://new.scoresaber.com/u/{ssid}",
                    description=
                    f"**Player Ranking:** [#{data['playerInfo']['rank']}](https://new.scoresaber.com/rankings/{grank}) \n**Country Ranking:** {data['playerInfo']['country']} [#{data['playerInfo']['countryRank']}](https://scoresaber.com/global/{crank}&country={data['playerInfo']['country']}) \n**Performance Points:** {data['playerInfo']['pp']}pp"
                )
                embed.color = self.bot.embed_color
                embed.set_thumbnail(
                    url=
                    f"https://new.scoresaber.com{data['playerInfo']['avatar']}"
                )
                embed.add_field(
                    name='Score Stats',
                    value=
                    f"**Play Count:** {data['scoreStats']['totalPlayCount']} \n**Ranked Play Count:** {data['scoreStats']['rankedPlayCount']} \n**Average Ranked Accuracy:** {data['scoreStats']['averageRankedAccuracy']:.2f}%",
                    inline=False)
                embed.set_footer(text='Powered by the ScoreSaber API')
                await message.edit(content=None, embed=embed)
        except KeyError:
            await ctx.send('The user is not in the database.')

    @ss.command(name='leaderboard',
                aliases=['top', 'ranking', 'lb'],
                help='Shows the top 12 players on the leaderboard right now.')
    async def lb(self, ctx):
        message = await ctx.send('Getting the leaderboard from ScoreSaber ...')
        async with self.bot.session.get(
                'https://new.scoresaber.com/api/players/1') as r:
            lb = await r.json()  # returns dict
        await message.edit(content='Got it! Sending top players ...')
        r = discord.Embed(title='ScoreSaber Leaderboard')
        tten = lb['players']
        for number, thing in enumerate(tten, 1):
            if number < 13:
                r.add_field(
                    name=f'#{number}: {tten[number-1]["playerName"]}',
                    value=
                    f'Performance Points: {tten[number-1]["pp"]}pp\nCountry: {tten[number-1]["country"]}\nRank Change: +{lb["players"][number-1]["difference"]}',
                    inline=True)
        r.set_footer(text='Powered by the ScoreSaber API')
        await message.edit(content=None, embed=r)

    @ss.command(name='register', help='Registers you to a ScoreSaber profile')
    async def reg(self, ctx, *, username: str):
        message = await ctx.send(f'Searching for `{username}` ...')
        username = urllib.parse.quote_plus(username.upper())
        username = username.replace('+', '%20')
        await message.edit(
            content=
            f'Searching for `{username}` ...\nFormatting `{username}` to use in the URL...'
        )
        async with self.bot.session.get(
                f'https://new.scoresaber.com/api/players/by-name/{username}'
        ) as url:
            url = await url.json()
            await message.edit(
                content=
                f'Searching for `{username}` ...\nFormatting `{username}` to use in the URL...\nGetting `{username}\'s` ID from API ...'
            )
            try:
                ssid = url['players'][0]['playerId']
                async with self.bot.session.get(
                        f"https://new.scoresaber.com/api/player/{ssid}/full"
                ) as data:
                    data = await data.json()
                await message.edit(
                    content=
                    f'Searching for `{username}` ...\nFormatting `{username}` to use in the URL...\nGetting `{username}\'s` ID from API ...\nGetting `{username}\'s` stats ...'
                )
                grank = math.ceil(int(data['playerInfo']['rank']) / 50)
                crank = math.ceil(int(data['playerInfo']['countryRank']) / 50)
                embed = discord.Embed(title="Is this you?",
                                      color=self.bot.embed_color)
                embed.set_thumbnail(
                    url=
                    f"https://new.scoresaber.com{data['playerInfo']['avatar']}"
                )
                embed.add_field(
                    name=data['playerInfo']['playerName'],
                    value=
                    f"**Player Ranking:** [#{data['playerInfo']['rank']}](https://new.scoresaber.com/rankings/{grank}) \n**Country Ranking:** {data['playerInfo']['country']} [#{data['playerInfo']['countryRank']}](https://scoresaber.com/global/{crank}&country={data['playerInfo']['country']}) \n**Performance Points:** {data['playerInfo']['pp']}pp",
                    inline=False)
                embed.set_footer(
                    text=
                    'React to this message with ✅ to confirm and ❌ to cancel')
                await message.edit(content=None, embed=embed, delete_after=15)
                await message.add_reaction('✅')
                await message.add_reaction('❌')

                def gcheck(reaction, user):
                    return user == ctx.author and str(
                        reaction.emoji) == '✅' or user == ctx.author and str(
                            reaction.emoji) == '❌'

                try:
                    reaction, user = await self.bot.wait_for('reaction_add',
                                                             timeout=14.0,
                                                             check=gcheck)
                except asyncio.TimeoutError:
                    await ctx.send('You did not react in time.')
                else:
                    if reaction.emoji == '✅':
                        await message.delete()
                        try:
                            await self.bot.scoresaber.insert_one({
                                "_id":
                                ctx.author.id,
                                "ssid":
                                ssid
                            })
                        except:
                            await self.bot.scoresaber.replace_one(
                                {"_id": ctx.author.id}, {"ssid": ssid})
                        await ctx.send(
                            f'Successfully registered ID `{ssid}` with <@{ctx.author.id}>'
                        )
                    if reaction.emoji == '❌':
                        await message.delete()
                        await ctx.send('Sorry that I could not help you.')
            except KeyError:
                await message.edit(content=url['error']['message'])

    @ss.command(name='unregister',
                help='Unregisters you from a ScoreSaber profile')
    async def ureg(self, ctx):
        e = discord.Embed(
            description='Would you like to remove yourself from the database?')
        e.set_footer(
            text='React to this message with ✅ to confirm and ❌ to cancel')
        embed = await ctx.send(embed=e, delete_after=15)
        await embed.add_reaction('✅')
        await embed.add_reaction('❌')

        def gcheck(reaction, user):
            return user == ctx.author and str(
                reaction.emoji) == '✅' or user == ctx.author and str(
                    reaction.emoji) == '❌'

        try:
            reaction, user = await self.bot.wait_for('reaction_add',
                                                     timeout=14.0,
                                                     check=gcheck)
        except asyncio.TimeoutError:
            await ctx.send('You did not react in time.')
        else:
            if reaction.emoji == '✅':
                e = discord.Embed(
                    description=
                    f'Sucessfully removed {ctx.author} and their corresponding ID from the database'
                )
                await self.bot.scoresaber.delete_one({"_id": ctx.author.id})
                await embed.edit(content=None, embed=e)
            if reaction.emoji == '❌':
                e = discord.Embed(description='Cancelled unregistering.')
                await embed.edit(content=None, embed=e, delete_after=15)

    @commands.command(name='key',
                      help='note: older songs do not show duration',
                      brief='Gets info about a song from BeatSaver')
    async def bsr(self, ctx, key: str):
        bad = ['Lawless', 'Lightshow']
        headers = {
            'User-Agent':
            'https://github.com/ppotatoo/pdbot, it is a discord bot coded in python',
        }
        async with self.bot.session.get(
                f'https://beatsaver.com/api/maps/detail/{key}',
                headers=headers) as data:
            data = await data.json()
            cortime = time.strftime('%H:%M:%S',
                                    time.gmtime(data['metadata']['duration']))
            embed = discord.Embed(
                title=data['name'],
                url=f"https://beatsaver.com/beatmap/{data['key']}",
                color=self.bot.embed_color)
            embed.set_thumbnail(url=f"https://beatsaver.com{data['coverURL']}")
            embed.add_field(name="Author",
                            value=f"{data['metadata']['songAuthorName']}",
                            inline=False)
            embed.add_field(name="Mapper",
                            value=f"{data['metadata']['levelAuthorName']}",
                            inline=False)
            embed.add_field(name="Uploader",
                            value=f"{data['uploader']['username']}",
                            inline=True)
            embed.add_field(name="Key", value=f"{data['key']}", inline=False)
            if data['metadata']['duration'] != 0:
                embed.add_field(name="Duration", value=f"{cortime}")
            bad = ['Lawless', 'Lightshow']
            charac = data['metadata']['characteristics'][0]['name']
            if charac in bad:
                embed.add_field(name="Playable on Quest?",
                                value="No",
                                inline=False)
            else:
                embed.add_field(name="Playable on Quest?",
                                value="Yes",
                                inline=False)
            embed.add_field(name="BPM",
                            value=f"{data['metadata']['bpm']:.1f}",
                            inline=False)
            embed.add_field(
                name="Download Link",
                value=f"https://beatsaver.com/api/download/key/{data['key']}",
                inline=False)
            embed.add_field(name="OneClick Install",
                            value=f"beatsaver://{data['key']}",
                            inline=True)
            embed.add_field(
                name="Preview",
                value=f"https://skystudioapps.com/bs-viewer/?id={data['key']}",
                inline=False)
            embed.set_footer(text='Powered by the BeatSaver API')
            await ctx.send(embed=embed)

    @bsr.error
    async def bsr_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please send a key along with the command.')
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send('Please send a valid key.')
        else:
            raise error


def setup(bot):
    bot.add_cog(BeatSaber(bot))
