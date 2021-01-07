from discord.ext import commands
import discord
import json

class prefixes(commands.Cog, command_attrs=dict(hidden=True)):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		with open('prefixes.json', 'r') as f:
			prefixes = json.load(f)

		prefixes[str(guild.id)] = '!'

		with open('prefixes.json', 'w') as f:
			json.dump(prefixes, f, indent=4)

	@commands.Cog.listner()
	async def on_guild_remove(self, guild):
		with open('prefixes.json', 'r') as f:
			prefixes = json.load(f)

		prefixes.pop(str(guild.id))

		with open('prefixes.json', 'w') as f:
			json.dump(prefixes, f, indent=4)

	@commands.command(name='changeprefix')
	async def prefix(self, ctx, prefix: str):
		with open('prefixes.json', 'r') as f:
			prefixes = json.load(f)

		prefixes[str(ctx.guild.id)] = prefix

		with open('prefixes.json', 'w') as f:
			json.dump(prefixes, f, indent=4)

def setup(bot):
	bot.add_cog(prefixes(bot))