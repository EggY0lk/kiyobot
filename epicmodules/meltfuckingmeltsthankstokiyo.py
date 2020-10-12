import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup

class MeltyScans(commands.Cog, name='Melty Scans'):
	def __init__(self, bot):
		self.bot = bot
		self.queuechan = 743713887123275817

	@commands.is_owner()
	@commands.command()
	async def queue(self, ctx, nhlink, raws = 'None', doclink = 'None', entitle = 'None', *en2):

		if en2 is None:
			pass
		else:
			en2 = ' '.join(en2)
			entitle = ' '.join((entitle,en2))
		if nhlink.startswith('https://nh'):
			pass
		else:
			try:
				nhcode = int(nhlink)
			except ValueError:
				await ctx.send(content='Error: Check your input')
				return
			nhlink = f'https://nhentai.net/g/{nhcode}'
		queuechannel = self.bot.get_channel(self.queuechan)
		pastqueue = await queuechannel.history(limit=1).flatten()
		prevmessage = pastqueue[0]
		if 'MS#' not in prevmessage.content:
			queuetag = '0001'
		else:
			queuetag = int(prevmessage.content[3:7]) + 1
			queuetag = f'{queuetag:04d}'
		firstpage = requests.get(nhlink)
		soup = BeautifulSoup(firstpage.text, 'html.parser')
		nhimg = requests.get(f'{nhlink}/1')
		imgsoup = BeautifulSoup(nhimg.text, 'html.parser')
		nhimglink = imgsoup.find('section', id='image-container').a.img['src']
		imgresp = requests.get(nhimglink)
		f = open("nhimage.jpg", "wb")
		f.write(imgresp.content)
		f.close()
		orititle = soup.find(id='info').h1.get_text()
		text = f'''MS#{queuetag} **{orititle}** --> {entitle}
NH link: <{nhlink}>
raw source: <{raws}>
TL link: <{doclink}>'''
		await queuechannel.send(content=text, file=discord.File('nhimage.jpg'))
		await ctx.send(f'Queued as MS#{queuetag}')

	@commands.is_owner()
	@commands.command()
	async def raw(self, ctx, id_, url):

		messages = await self.bot.get_channel(self.queuechan).history().flatten()
		for message in messages:
			if f'MS#{id_}' in message.content:
				oldcontent = message.content.split('\n')
				for line in oldcontent:
					if 'raw' in line:
						newcontent = message.content.replace(line, f'raw source: <{url}>')
				await message.edit(content=newcontent)
				await ctx.message.add_reaction('👌')

	@commands.is_owner()
	@commands.command()
	async def doc(self, ctx, id_, url):

		messages = await self.bot.get_channel(self.queuechan).history().flatten()
		for message in messages:
			if f'MS#{id_}' in message.content:
				oldcontent = message.content.split('\n')
				for line in oldcontent:
					if 'TL link' in line:
						newcontent = message.content.replace(line, f'TL link: <{url}>')
				await message.edit(content=newcontent)
				await ctx.message.add_reaction('👌')

	@commands.is_owner()
	@commands.command()
	async def title(self, ctx, id_, *title):

		title = ' '.join(title)
		messages = await self.bot.get_channel(self.queuechan).history().flatten()
		for message in messages:
			if f'MS#{id_}' in message.content:
				oldcontent = message.content.split('\n')[0]
				oldline = oldcontent.split(' --> ')
				newline = oldline[0] + ' --> ' + title
				newcontent = message.content.replace(oldcontent, newline)
				await message.edit(content=newcontent)
				await ctx.message.add_reaction('👌')
	
	@commands.is_owner()
	@commands.command()
	async def cancel(self, ctx, id_):

		messages = await self.bot.get_channel(self.queuechan).history().flatten()
		for message in messages:
			if f'MS#{id_}' in message.content:
				if message.content.endswith('~~'):
					await ctx.send(content='Doujin already cancelled')
					return
				if message.content.endswith('✅'):
					await ctx.send(content='Doujin already finished')
					return
				await message.edit(content=f'MS#{id_} ~~{message.content[8:]}~~')
				await ctx.message.add_reaction('👌')
	
	@commands.is_owner()
	@commands.command()
	async def done(self, ctx, id_):

		messages = await self.bot.get_channel(self.queuechan).history().flatten()
		for message in messages:
			if f'MS#{id_}' in message.content:
				if message.content.endswith('~~'):
					await ctx.send(content='Doujin already cancelled')
				elif message.content.endswith('✅'):
					await ctx.send(content='Doujin already finished')
					return
				await message.edit(content=f'{message.content} ✅')
				await ctx.message.add_reaction('👌')

def setup(bot):
	bot.add_cog(MeltyScans(bot))