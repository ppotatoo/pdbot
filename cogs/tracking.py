from discord.ext import commands
import discord
import random
import traceback
import sys

class tracking(commands.Cog, command_attrs=dict(hidden=True)):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_message(self, message):
		if not message.guild:
			if message.author.id == self.bot.user.id:
				return
			else:
				channel = self.bot.get_channel(788471476927332382)
				creationtime = message.created_at
				embed = discord.Embed(title='*INCOMEING MESSAGE*', description=f'{message.author.mention} sent `{message.content}`')
				embed.colour = 0xFFFFFF
				embed.set_thumbnail(url=message.author.avatar_url)
				embed.set_footer(text=f"Sent at {creationtime}	ID: {message.author.id}")
				embed.set_author(name=f'{message.author}', url='https://www.urbandictionary.com/define.php?term=Your%20mum%20gay', icon_url=f'{message.author.avatar_url}')
				await channel.send(embed=embed)
				return

	@commands.Cog.listener()
	async def on_command(self, ctx):
		channel = self.bot.get_channel(788471476927332382)
		embed2 = discord.Embed(title='Command Use')
		embed2.color = discord.Colour.from_hsv(random.random(), 1, 1) #0x2f3136 is the gray color that blends in
		#embed2.set_thumbnail(url=ctx.author.avatar_url)
		embed2.set_footer(text=f"Sent at {ctx.message.created_at}")
		embed2.add_field(name='Command', value=f'{ctx.message.content}', inline=False)
		embed2.add_field(name='Where', value=f'#{ctx.channel}, ID = {ctx.channel.id}, Guild = {ctx.guild}')
		embed2.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
		embed2.set_footer(text=f'Sent at {ctx.message.created_at}')

		await channel.send(embed=embed2)

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		"""The event triggered when an error is raised while invoking a command.
        Parameters
        ------------
        ctx: commands.Context
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
        """

        # This prevents any commands with local handlers being handled here in on_command_error.
		if hasattr(ctx.command, 'on_error'):
			return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
		cog = ctx.cog
		if cog:
			if cog._get_overridden_method(cog.cog_command_error) is not None:
				return

		ignored = (commands.CommandNotFound, )

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
		error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
		if isinstance(error, ignored):
			return

		if isinstance(error, commands.DisabledCommand):
			await ctx.send(f'{ctx.command} has been disabled.')

		elif isinstance(error, commands.NoPrivateMessage):
			try:
				await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
			except discord.HTTPException:
				pass

        # For this error example we check to see where it came from...
		elif isinstance(error, commands.BadArgument):
				if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
					await ctx.send('I could not find that member. Please try again.')

		else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
			print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
			traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def setup(bot):
	bot.add_cog(tracking(bot))
