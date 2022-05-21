import io
import discord
from discord import app_commands
from datetime import datetime
import os
import httpx


def getKeyFile():
    keyFile = "botkey.txt"
    if not os.path.exists(keyFile):
        file = open(keyFile, "w")
        botKey = "Enter Your bot key here"
        file.write(botKey)
        print("Please Update the bot key")
        exit()
    else:
        file = open(keyFile, "r")
        botKey = file.readline()
        return botKey


def getTime():
    now = datetime.now()
    currentTime = now.strftime("%m/%d/%y | %H:%M:%S")
    return currentTime


async def getBytesOfURL(url):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        return r


# Returns true if the size of the file is under discords upload threshold for default servers
def checkFileSize(Bytes):
    return len(Bytes.content) <= 8388608


class client(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False  # we use this so the bot doesn't sync commands more than once

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:  # check if slash commands have been synced
            await tree.sync(guild=discord.Object(id=testServerID))
            self.synced = True
        print('Started at: ' + getTime())


bot = client()
tree = app_commands.CommandTree(bot)
testServerID = 964780178201010226
verifiedUsers = [614557040102342677, 964776764037550100]
defaultChannelID = 964792135087951872
magicNumbers = {'.png': bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]),
                '.jpg': bytes([0xFF, 0xD8, 0xFF, 0xE1]),
                'jpg': bytes([0xFF, 0xD8, 0xFF, 0xE0]),
                '.gif': bytes([0x47, 0x49, 0x46, 0x38]),
                '.webp': bytes([0x52, 0x49, 0x46, 0x46]),
                '.mp4': bytes([0x00, 0x00, 0x00, 0x20, 0x66, 0x74, 0x79, 0x70]),
                'mp4': bytes([0x00, 0x00, 0x00, 0x1c, 0x66, 0x74, 0x79, 0x70]),
                '.mov': bytes([0x00, 0x00, 0x00, 0x14, 0x66, 0x74, 0x79, 0x70]),
                }


def getDefaultChannel():
    return bot.get_channel(defaultChannelID)


def getFileName(filename, RB, spoiler):
    if spoiler:
        return f"SPOILER_{filename}{getFileExtensionType(RB.content)}"
    else:
        return f"{filename}{getFileExtensionType(RB.content)}"


def getFileExtensionType(fileBytes):
    for ext in magicNumbers:
        if fileBytes.startswith(magicNumbers[ext]):
            if ext == "jpg":
                ext = ".jpg"
            if ext == "mp4":
                ext = ".mp4"
            return ext


def checkUser(checkId):
    for id in verifiedUsers:
        return checkId == id


def translateBytesIntoKB(incomingBytes):
    return incomingBytes / 1024


def translateBytesIntoMB(incomingBytes):
    return incomingBytes / 1048576


def getFileSize(RB):
    ByteValue = len(RB)
    if ByteValue <= 1024:
        return f"{ByteValue} Bytes"
    elif ByteValue <= 1048576:
        return f"{'%.2f' % translateBytesIntoKB(ByteValue)} KB"
    else:
        return f"{'%.2f' % translateBytesIntoMB(ByteValue)} MB"


@tree.command(guild=discord.Object(id=testServerID), name='createchannel', description='Creates a Channel')
@app_commands.describe(catergory='The catergory to create it in.')
@app_commands.describe(channelname='Name of the channel to be made')
async def slash1(interaction: discord.Interaction, catergory: discord.CategoryChannel, channelname: str):
    if checkUser(interaction.user.id):
        await catergory.create_text_channel(channelname)
        for channel in catergory.channels:
            if channel.name == channelname:
                id = channel.id
        await interaction.response.send_message(f"Created <#{id}> at {getTime()}", ephemeral=True)  # ephemeral means "locally" sent to client.
    else:
        await interaction.response.send_message(f"You do not have the proper perms for this bot.")


@tree.command(guild=discord.Object(id=testServerID), name='changeperms', description='Enables and Disables Certain Perms')
@app_commands.describe(deleteperms='Delete Perms On/OFF')
@app_commands.describe(viewperms='View Perms On/OFF')
@app_commands.describe(adminperms='Admin Perms On/OFF')
async def slash1(interaction: discord.Interaction, deleteperms: bool = False, viewperms: bool = False, adminperms: bool = False):
    if checkUser(interaction.user.id):
        await interaction.response.send_message(f"Roles updated at {getTime()}", ephemeral=True)
        if deleteperms:
            await interaction.user.add_roles(interaction.guild.get_role(977645698306695198))
        else:
            await interaction.user.remove_roles(interaction.guild.get_role(977645698306695198))
        if viewperms:
            await interaction.user.add_roles(interaction.guild.get_role(977645908776874096))
        else:
            await interaction.user.remove_roles(interaction.guild.get_role(977645908776874096))
        if adminperms:
            await interaction.user.add_roles(interaction.guild.get_role(977651225380151328))
        else:
            await interaction.user.remove_roles(interaction.guild.get_role(977651225380151328))
    else:
        await interaction.response.send_message(f"You do not have the proper perms for this bot.")


@tree.command(guild=discord.Object(id=testServerID), name='upload', description='Upload Files')  # guild specific slash command
@app_commands.describe(channel='The channel to Send it in.')
@app_commands.describe(filename='Name of the File')
@app_commands.describe(url='Url of the Image')
@app_commands.describe(source='Url of the Source')
async def slash1(interaction: discord.Interaction, url: str, filename: str, spoiler: bool = False, channel: discord.TextChannel = None, source: str = None):
    if checkUser(interaction.user.id):
        returnedBytes = await getBytesOfURL(url)
        if channel is None:
            channel = getDefaultChannel()
        if source is None:
            if checkFileSize(returnedBytes):
                await interaction.response.send_message(f"Completed File Download Successfully at {getTime()}, Uploading {getFileSize(returnedBytes.content)} of content.", ephemeral=True)  # ephemeral means "locally" sent to client.
                await channel.send(f"Uploaded `{filename}` at `{getTime()}` \n`{url}`", file=discord.File(io.BytesIO(returnedBytes.content), filename=getFileName(filename, returnedBytes, spoiler)))
            else:
                await interaction.response.send_message(f"Completed File Download Successfully at {getTime()}, Unable to upload {getFileSize(returnedBytes.content)} of content.", ephemeral=True)
                await channel.send(f"Attempted Upload of `{filename}` at `{getTime()}` \n{url}")
        else:
            if checkFileSize(returnedBytes):
                await interaction.response.send_message(f"Completed File Download Successfully at {getTime()}, Uploading {getFileSize(returnedBytes.content)} of content.", ephemeral=True)  # ephemeral means "locally" sent to client.
                await channel.send(f"Uploaded `{filename}` at `{getTime()}` \n`{url}`\nSource: `{source}`", file=discord.File(io.BytesIO(returnedBytes.content), filename=getFileName(filename, returnedBytes, spoiler)))
            else:
                await interaction.response.send_message(f"Completed File Download Successfully at {getTime()}, Unable to upload {getFileSize(returnedBytes.content)} of content.", ephemeral=True)
                await channel.send(f"Attempted Upload of `{filename}` at `{getTime()}` \n{url}\nSource: `{source}`")

    else:
        await interaction.response.send_message(f"You do not have the proper perms for this bot.")


@tree.command(guild=discord.Object(id=testServerID), name='avatar', description='Uploads Avatars')  # guild specific slash command
@app_commands.describe(channel='The channel to Send it in.')
@app_commands.describe(userid='ID of the User')
async def slash1(interaction: discord.Interaction, userid: str, spoiler: bool = False, channel: discord.TextChannel = None):
    if checkUser(interaction.user.id):
        discUser = await client.fetch_user(bot, userid)
        userAvatarURL = discUser.avatar.url
        returnedBytes = await getBytesOfURL(userAvatarURL)
        if channel is None:
            channel = getDefaultChannel()
        if checkFileSize(returnedBytes):
            await interaction.response.send_message(f"Completed File Download Successfully at {getTime()}, Uploading {getFileSize(returnedBytes.content)} of content.", ephemeral=True)  # ephemeral means "locally" sent to client.
            await channel.send(f"Uploaded `{discUser.name}` | `{discUser.id}` | <@{discUser.id}> at `{getTime()}` \n`{userAvatarURL}`", file=discord.File(io.BytesIO(returnedBytes.content), filename=getFileName(discUser.name, returnedBytes, spoiler)))
        else:
            await interaction.response.send_message(f"Completed File Download Successfully at {getTime()}, Unable to upload {getFileSize(returnedBytes.content)} of content.", ephemeral=True)
            await channel.send(f"Attempted Upload of `{discUser.name}` at `{getTime()}` \n{userAvatarURL}")
    else:
        await interaction.response.send_message(f"You do not have the proper perms for this bot.")


@tree.command(guild=discord.Object(id=testServerID), name='banner', description='Uploads Banners')  # guild specific slash command
@app_commands.describe(channel='The channel to Send it in.')
@app_commands.describe(userid='ID of the User')
async def slash1(interaction: discord.Interaction, userid: str, spoiler: bool = False, channel: discord.TextChannel = None):
    if checkUser(interaction.user.id):
        discUser = await client.fetch_user(bot, userid)
        userBannerURL = discUser.banner.url
        returnedBytes = await getBytesOfURL(userBannerURL)
        if channel is None:
            channel = getDefaultChannel()
        if checkFileSize(returnedBytes):
            await interaction.response.send_message(f"Completed File Download Successfully at {getTime()}, Uploading {getFileSize(returnedBytes.content)} of content.", ephemeral=True)  # ephemeral means "locally" sent to client.
            await channel.send(f"Uploaded `{discUser.name}` | `{discUser.id}` | <@{discUser.id}> at `{getTime()}` \n`{userBannerURL}`", file=discord.File(io.BytesIO(returnedBytes.content), filename=getFileName(discUser.name, returnedBytes, spoiler)))
        else:
            await interaction.response.send_message(f"Completed File Download Successfully at {getTime()}, Unable to upload {getFileSize(returnedBytes.content)} of content.", ephemeral=True)
            await channel.send(f"Attempted Upload of `{discUser.name}` at `{getTime()}` \n{userBannerURL}")
    else:
        await interaction.response.send_message(f"You do not have the proper perms for this bot.")


bot.run(getKeyFile())
