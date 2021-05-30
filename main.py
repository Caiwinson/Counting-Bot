import discord
import json
from discord.ext import commands
from discord.utils import get
import asyncio
from discord.ext.commands import MissingPermissions

with open('config.json', 'r') as f:
    config = json.load(f)

token = config['token']
pre = config['prefix']
client = commands.Bot(command_prefix=pre)
client.remove_command('help')

@client.event
async def on_ready():
	await client.change_presence(activity=discord.Game(f'{pre}help'))
	print("ready")

@client.command()
@commands.has_permissions(manage_channels=True)
async def start(ctx):
	with open('count.json', 'r') as f:
		count = json.load(f)
	if str(ctx.guild.id) in count:
		await ctx.send("You can only create 1 counting channel per server")
		return
	if not str(ctx.guild.id) in count:
		await ctx.send("Creating channel\nWhat's the name of the channel")

		def check(msg):
			return msg.author == ctx.author and ctx.channel

		channel_name = (await client.wait_for('message', check=check)).content
		count_channel = await ctx.guild.create_text_channel(name=channel_name)
		await count_channel.set_permissions(client.user,
		                                    read_messages=True,
		                                    send_messages=True,
		                                    view_channel=True,
		                                    add_reactions=True,
		                                    manage_messages=True)
		count[f"{ctx.guild.id}"] = {}
		count[f"{ctx.guild.id}"]['channel'] = count_channel.id
		count[f"{ctx.guild.id}"]['latest'] = 0
		count[f"{ctx.guild.id}"]['amount'] = 2
		count[f"{ctx.guild.id}"]['ResetOnFail'] = str(True)
		count[f"{ctx.guild.id}"]['CountMore'] = "False"
		with open('count.json', 'w') as f:
			json.dump(count, f, indent=4)
		await ctx.send(
		    f"<#{count_channel.id}> has been created\nStart counting from 1")
		await asyncio.sleep(1)
		check_react = await count_channel.send("1")
		await check_react.add_reaction("✅")


@client.command()
async def help(ctx):
	embed = discord.Embed(
	    title=f"{pre}help",
	    description=
	    f"All of the command can only be executed with manage channel perm\nExcept for {pre}invite",
	    colour=0x3b88c3)
	embed.add_field(
	    name=f"{pre}start",
	    value=
	    "Create a new counting channel for your server\nYou can only have 1 counting channel per server",
	    inline=False)
	embed.add_field(name=f"{pre}invite",
	                value="Invite {client.user.mention} to your server",
	                inline=False)
	embed.set_footer(text="Bot created by Cai winson#2131")
	await ctx.send(embed=embed)

@client.command()
@commands.has_permissions(manage_channels=True)
async def settings(ctx, setting=None, tf=None):
	with open('count.json', 'r') as f:
		count = json.load(f)
	if not setting:
		if str(ctx.guild.id) in count:
			embed = discord.Embed(title=f"{pre}settings", colour=0x3b88c3)
			embed.add_field(
			    name=f"{pre}settings ResetOnFail True/False",
			    value=
			    f"if user send the wrong number\n the streak will be reseted\n```ResetOnfail={count[str(ctx.guild.id)]['ResetOnFail']}```"
			)
			embed.add_field(
			    name=f"{pre}settings Delete",
			    value="delete counting channel if you have a problem")
			embed.add_field(
			    name=f"{pre}settings CountMore True/False",
			    value=
			    f"Let user count more than once\n```Countmore={count[str(ctx.guild.id)]['CountMore']}```"
			)
			embed.set_footer(text="Bot created by Cai winson#2131")
			await ctx.send(embed=embed)
			return
		if str(ctx.guild.id) in count:
			await ctx.send(
			    f"No counting channel is made\nType {pre} to create a counting channel"
			)
	if setting:
		if setting == "ResetOnFail":
			if tf == "True":
				count[f"{ctx.guild.id}"]['ResetOnFail'] = "True"
				await ctx.send("ResetOnFail set to True")
			if tf == "False":
				count[f"{ctx.guild.id}"]['ResetOnFail'] = "False"
				await ctx.send("ResetOnFail set to False")
		if setting == "Delete":
			await ctx.send(
			    f"<#{count[str(ctx.guild.id)]['channel']}> is no longer a counting channel"
			)
			count.pop(str(ctx.guild.id))
		if setting == "CountMore":
			if tf == "True":
				count[f"{ctx.guild.id}"]['CountMore'] = "True"
				await ctx.send("CountMore set to True")
			if tf == "False":
				count[f"{ctx.guild.id}"]['CountMore'] = "False"
				await ctx.send("CountMore set to False")
	with open('count.json', 'w') as f:
		json.dump(count, f, indent=4)


@client.event
async def on_message(message):
	if message.author == client.user:
		return
	if message.guild is not None:
		with open('count.json', 'r') as f:
			count = json.load(f)
		if str(message.guild.id) in count:
			amount = count[str(message.guild.id)]['amount']
			latest = count[str(message.guild.id)]['latest']
			count_channel = client.get_channel(count[str(
			    message.guild.id)]['channel'])
			CountMore = count[str(message.guild.id)]['CountMore']
			ResetOnFail = count[str(message.guild.id)]['ResetOnFail']
			if count_channel == message.channel:
				if CountMore == "False":
					if ResetOnFail == "True":
						if message.author.id == latest:
							await message.add_reaction(
							    "<:warningsign:847330302640521240>")
							await message.channel.send(
							    f"{message.author.mention} screwed up at {amount}\nYou can't count twice\nStart Counting from 1 again"
							)
							count[str(message.guild.id)]['amount'] = 1
							count[str(message.guild.id)]['latest'] = 0
							with open('count.json', 'w') as f:
								json.dump(count, f, indent=4)
							return
					if ResetOnFail == "False":
						if message.author.id == latest:
							await message.delete()
							await message.channel.send("You can't count twice",
							                           delete_after=10)
							return
				if CountMore == "True":
					pass
				if not message.content.startswith(f"{amount}"):
					if ResetOnFail == "True":
						await message.add_reaction(
						    "<:warningsign:847330302640521240>")
						await message.channel.send(
						    f"{message.author.mention} screwed up at {amount}\nYou sent the wrong number\nStart Counting from 1 again"
						)
						count[str(message.guild.id)]['amount'] = 1
						count[str(message.guild.id)]['latest'] = 0
						with open('count.json', 'w') as f:
							json.dump(count, f, indent=4)
						return
					if ResetOnFail == "False":
						await message.channel.send(
						    f"Wrong Number:warning:\nThe next number is **{amount}**",
						    delete_after=10)
						await message.delete()
				if message.content.startswith(f"{amount}"):
					count[str(message.guild.id)]['amount'] += 1
					count[str(message.guild.id)]['latest'] = message.author.id
					await message.add_reaction("✅")
					with open('count.json', 'w') as f:
						json.dump(count, f, indent=4)
					return
			if not count_channel == message.channel:
				await client.process_commands(message)

		else:
			await client.process_commands(message)

@settings.error
async def settings_error(ctx, error):
	if isinstance(error, MissingPermissions):
		text = "Sorry {}, you do not have permissions to do that!".format(
		    ctx.message.author.mention)
		await ctx.send(text)

@start.error
async def start_error(ctx, error):
	if isinstance(error, MissingPermissions):
		text = "Sorry {}, you do not have permissions to do that!".format(
		    ctx.message.author.mention)
		await ctx.send(text)

client.run(token)
