import discord
from discord.ext import commands
from random import randint, choice
from sauce_finder import sauce_finder
import nhentai as nh

class Danboorushit(commands.Cog, name='Danbooru'):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.db = bot.db
	
	@commands.is_nsfw()
	@commands.command()
	async def latest(self, ctx: commands.Bot, key: str = None, *tag: str):
		'''shits out latest danbooru pic (kiyo by default)'''
		if key is None:
			tag="kiyohime_(fate/grand_order)"
		else:
			tag = '_'.join(tag)
			tag = key + '_' + tag
		post = self.db.post_list(tags=tag, page=1, limit=1)[0]
		try:
			fileurl = post['file_url']
		except:
			fileurl = 'https://danbooru.donmai.us' + post['source']
		e = discord.Embed(title="Latest", color=0x00FF00)
		e.set_image(url=fileurl)
		await ctx.send(embed=e)
	
	@commands.is_nsfw()
	@commands.command(aliases=['dan','d'])
	async def danbooru(self, ctx: commands.Context, *tag: str):
		'''Finds an image on danbooru'''
		page = randint(1,5)
		try:
			posts = self.db.post_list(tags=tag,page=page,limit=5)
			post = choice(posts)
			try:
				fileurl = post['file_url']
			except KeyError:
				fileurl = 'https://danbooru.donmai.us' + post['source']
			e = discord.Embed(color=0x0000ff)
			e.set_image(url=fileurl)
			await ctx.send(embed=e)
		except:
			await ctx.send(content="Can't find image! Please enter in this format `character name (series)`")

	@commands.is_nsfw()
	@commands.command()
	async def multi(self, ctx: commands.Context, *, tag: str):
		'''Finds multiple images on danbooru'''
		page = randint(1,5)
		e = discord.Embed(color=0x00FFBE)
		try:
			posts = self.db.post_list(tags=tag,page=page,limit=5)
			for post in posts:
				try:
					fileurl = post['file_url']
				except KeyError:
					fileurl = 'https://danbooru.donmai.us' + post['source']
				e.set_image(url=fileurl)
				await ctx.send(embed=e)
		except:
			await ctx.send(content="Some shit broke. Also firara is gay")
	
	@commands.command()
	async def iqdb(self, ctx: commands.Context, url: str = None):
		'''finds image sauce on iqdb'''
		if url is None:
			url = ctx.message.attachments[0].url
		result = sauce_finder.get_match(url)
		if result['type'] == 'possible':
			thing = result['found'][0]
		else:
			thing = result['found']
		if thing['rating'] == '[Explicit]' and not ctx.channel.is_nsfw():
			await ctx.send("Explicit result")
			return
		await ctx.send(content=f"{result['type']} result: {thing['link']}")

	@commands.command(aliases=['nao', 'sauce'])
	async def saucenao(self, ctx: commands.Context, url: str = None):
		'''finds image sauce on saucenao'''
		if url is None:
			url = ctx.message.attachments[0].url
		results = await self.bot.sauce.from_url(url)
		if len(results) == 0:
			await ctx.send(content="No results found.")
			return
		await ctx.send(content=f'Similarity: {results[0].similarity}\n{results[0].url}')
	
	@commands.is_nsfw()
	@commands.group(aliases=['nh'], invoke_without_command=True)
	async def nhentai(self, ctx: commands.Context, djid: int):
		'''finds doujins on nhentai by id'''
		if ctx.invoked_subcommand is not None:
			return
		result = nh.get_doujin(djid)
		tags = [_.name for _ in result.tags]
		e = discord.Embed(title=result.titles['pretty'], description=f'#{result.id}', url=result.url, color=0x177013)
		e.set_image(url=result.cover)
		e.add_field(name="Tags", value=', '.join(tags))
		await ctx.send(embed=e)
	
	@nhentai.error
	async def nh_error(self, ctx: commands.Context, error):
		rep = ctx.message.content.replace(f'{ctx.prefix}{ctx.invoked_with}', f'{ctx.prefix}{ctx.invoked_with} search')
		await ctx.send(f"Invalid doujin id, did you mean `{rep}`")

	@commands.is_nsfw()
	@nhentai.command()
	async def random(self, ctx: commands.Context):
		'''finds random doujin'''
		await self.nhentai(ctx, nh.get_random_id())

	@commands.is_nsfw()
	@nhentai.command(aliases=['find'])
	async def search(self, ctx: commands.Context, *, tags: str):
		'''finds doujins by tags'''
		djid = choice(nh.search(tags)).id
		await self.nhentai(ctx, djid)

	@search.error
	async def random_error(self, ctx, error):
		await ctx.send('No results found!')

def setup(bot: commands.Bot):
	bot.add_cog(Danboorushit(bot))