import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext

import inspirobot

class Slash(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@cog_ext.cog_slash(description='get inspired, kids')
	async def inspire(self, ctx: SlashContext):
		quote = inspirobot.generate()
		await ctx.send(content=quote.url)

	@cog_ext.cog_slash(description='google for stuff here')
	async def google(self, ctx: SlashContext, *, query):
		comm = self.bot.get_cog('Google').google
		await comm(ctx=ctx, query=query)
	
	@cog_ext.cog_subcommand(base="google", name="image")
	async def _google_image(self, ctx: SlashContext, *, query):
		comm = self.bot.get_cog('Google').image
		await comm(ctx=ctx, query=query)

	@cog_ext.cog_slash(description="calculates stuff")
	async def calculate(self, ctx: SlashContext, *, question):
		comm = self.bot.get_cog('Google').calculate
		await comm(ctx=ctx, query=question)

def setup(bot: commands.Bot):
	bot.add_cog(Slash(bot))