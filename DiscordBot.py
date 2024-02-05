import discord
from discord.ext import commands
from datetime import datetime

intents = discord.Intents.default()
intents.reactions = True
intents.presences = True
intents.guilds = True
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix='/', intents=intents)

user_tasks = {}
task_output_channel_id = 1202685135892250644  # Replace with your actual output channel ID
bot_token = 'INSERT_TOKEN_HERE'

@bot.event
async def on_ready():
    await bot.tree.sync()

#### MESSAGE DELETION #####
@bot.event
async def on_message(message):
    if message.author.bot or message.content.startswith('/') or message.channel.id != task_output_channel_id:
        return
    try:
        await message.delete()
        print(f"Deleted a message from {message.author} in {message.channel}: {message.content}")
    except discord.Forbidden:
        print(f"I don't have permissions to delete messages:\n{message}.")


#### TASK ASSIGNMENT #####
@bot.tree.command(name="assign", description="Assign yourself a new task")
async def set_task(interaction: discord.Interaction, task: str):
    user_tasks[interaction.user.id] = task
    output_channel = bot.get_channel(task_output_channel_id)

    if output_channel:
        assignment_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        embed = discord.Embed(title="Task Assignment", color=discord.Color.blue())
        embed.add_field(name="Assigned To", value=interaction.user.display_name, inline=False)
        embed.add_field(name="Task", value=task, inline=False)
        embed.add_field(name="Assignment Time", value=assignment_time, inline=False)
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="unassign", description="Unassign from your task")
async def unassign_task(interaction: discord.Interaction):
    output_channel = bot.get_channel(task_output_channel_id)
    if user_tasks.pop(interaction.user.id, None):
        embed = discord.Embed(title="Task Unassigned", color=discord.Color.red())
        embed.add_field(name="User", value=interaction.user.display_name, inline=False)
        embed.add_field(name="Status", value="Task completed and unassigned.", inline=False)
        
        if output_channel:
            await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Task unassigned", description="There are currently no tasks assigned to you.", color=discord.Color.light_gray())
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="listtasks", description="List all ongoing tasks in the project")
async def list_tasks(interaction: discord.Interaction):
    if user_tasks:
        embed = discord.Embed(title="Current Tasks", color=discord.Color.gold())
        for user_id, task in user_tasks.items():
            user = await bot.fetch_user(user_id)
            user_name = user.display_name if user else 'Unknown User'
            embed.add_field(name=user_name, value=task, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title="No Tasks Assigned", description="There are currently no tasks assigned to you.", color=discord.Color.light_gray())
        await interaction.response.send_message(embed=embed, ephemeral=True)


#### RUN THE BOT ####
bot.run(bot_token)
