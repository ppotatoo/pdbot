from discord.ext import commands
import discord
import requests
import urllib.parse
import time
import math

class BeatSaber(commands.Cog, name='Beat Saber', command_attrs=dict(hidden=False)):
	'''Beat Saber Related Commands'''
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='ss', help='As long as your username doesn\'t contain \'+\'')
	async def info(self, ctx, *, username: str):
		message = await ctx.send(f'Searching for `{username}` ...')
		username = urllib.parse.quote_plus(username.upper())
		username = username.replace('+', '%20')
		await message.edit(content=f'Searching for `{username}` ...\nFormatting `{username}` to use in the URL...')
		url = requests.get(f'https://new.scoresaber.com/api/players/by-name/{username}').json()
		await message.edit(content=f'Searching for `{username}` ...\nFormatting `{username}` to use in the URL...\nGetting `{username}\'s` ID from API ...')
		try:
			ssid = url['players'][0]['playerId']
			data = requests.get(f"https://new.scoresaber.com/api/player/{ssid}/full").json()
			await message.edit(content=f'Searching for `{username}` ...\nFormatting `{username}` to use in the URL...\nGetting `{username}\'s` ID from API ...\nGetting `{username}\'s` stats ...')
			grank = math.ceil(int(data['playerInfo']['rank'])/50)
			crank = math.ceil(int(data['playerInfo']['countryRank'])/50)
			embed = discord.Embed(title=f"{data['playerInfo']['playerName']}\'s Profile", url=f"https://new.scoresaber.com/u/{ssid}", description=f"**Player Ranking:** [#{data['playerInfo']['rank']}](https://new.scoresaber.com/rankings/{grank}) \n**Country Ranking:** {data['playerInfo']['country']} [#{data['playerInfo']['countryRank']}](https://new.scoresaber.com/rankings/{crank}https://scoresaber.com/global/{crank}&country={data['playerInfo']['country']}) \n**Performance Points:** {data['playerInfo']['pp']}")
			embed.color = 0x2f3136
			embed.set_thumbnail(url=f"https://new.scoresaber.com{data['playerInfo']['avatar']}")
			embed.add_field(name='Score Stats', value=f"**Play Count:** {data['scoreStats']['totalPlayCount']} \n**Ranked Play Count:** {data['scoreStats']['rankedPlayCount']} \n**Average Ranked Accuracy:** {data['scoreStats']['averageRankedAccuracy']:.2f}%", inline=False)
			embed.set_footer(text=f'Powered by the ScoreSaber API')
			await message.edit(content=None, embed=embed)
		except KeyError:
			await message.edit(content='Player not found.')

	@commands.command(name='key', help='!key <keyfrombeatsaver> note: older songs do not show duration')
	async def bsr(self, ctx, key: str):
		bad = ['Lawless', 'Lightshow']
		headers = {
    		'User-Agent': 'https://github.com/ppotatoo/pdbot, it is a discord bot coded in python',
				}
		data = requests.get(f'https://beatsaver.com/api/maps/detail/{key}', headers=headers).json()
		cortime = time.strftime('%H:%M:%S', time.gmtime(data['metadata']['duration']))
		embed = discord.Embed(title=data['name'], url=f"https://beatsaver.com/beatmap/{data['key']}")
		embed.color = 0x2f3136
		embed.set_thumbnail(url=f"https://beatsaver.com{data['coverURL']}")
		embed.add_field(name=f"Author", value=f"{data['metadata']['songAuthorName']}", inline=False)
		embed.add_field(name=f"Mapper", value=f"{data['metadata']['levelAuthorName']}", inline=False)
		embed.add_field(name=f"Uploader", value=f"{data['uploader']['username']}", inline=True)
		embed.add_field(name=f"Key", value=f"{data['key']}", inline=False)
		if data['metadata']['duration'] != 0:
			embed.add_field(name=f"Duration", value=f"{cortime}")
		bad = ['Lawless', 'Lightshow']
		charac = data['metadata']['characteristics'][0]['name']
		if charac in bad:
			embed.add_field(name=f"Playable on Quest?", value=f"No", inline=False)
		else:
			embed.add_field(name=f"Playable on Quest?", value=f"Yes", inline=False)
		embed.add_field(name=f"BPM", value=f"{data['metadata']['bpm']}", inline=False)
		embed.add_field(name=f"Download Link", value=f"https://beatsaver.com/api/download/key/{data['key']}", inline=False)
		embed.add_field(name=f"OneClick Install", value=f"beatsaver://{data['key']}", inline=True)
		embed.add_field(name=f"Preview", value=f"https://skystudioapps.com/bs-viewer/?id={data['key']}", inline=False)
		embed.set_footer(text=f'Powered by the BeatSaver API')
		await ctx.send(embed=embed)

	@bsr.error
	async def bsr_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send('Please send a key along with the command.')
		else:
			raise error	


def setup(bot):
	bot.add_cog(BeatSaber(bot))