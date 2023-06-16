import io
import re

import discord
from discord import app_commands
from utils import getTime, getBotKey, checkAndSetupConfigFile, getMainGuildID, getDefaultChannelID, getDeletePermsRoleID, getViewPermsRoleID, getAdminPermsRoleID, getOwnerID
from filesutils import getBytesOfURL, checkFileSize, getFileSize, getFileName, adjustPictureSizeDiscord, getHashOfBytes, getBasicFileName

# Complete Startup Steps
checkAndSetupConfigFile()


class client(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False  # we use this so the bot doesn't sync commands more than once

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:  # check if slash commands have been synced
            await tree.sync(guild=discord.Object(id=serverID))
            self.synced = True
        print('Started at: ' + getTime())


bot = client()
tree = app_commands.CommandTree(bot)
serverID = int(getMainGuildID())
defaultChannelID = int(getDefaultChannelID())
deletePermsRoleID = int(getDeletePermsRoleID())
viewPermsRoleID = int(getViewPermsRoleID())
adminPermsRoleID = int(getAdminPermsRoleID())
updatedDefaultChannel = None
ownerID = int(getOwnerID())


def getDefaultChannel():
    if updatedDefaultChannel is None:
        return bot.get_channel(int(defaultChannelID))
    else:
        return bot.get_channel(int(updatedDefaultChannel))


@tree.command(guild=discord.Object(id=serverID), name='createchannel', description='Creates a Channel')
@app_commands.describe(category='The category to create it in.')
@app_commands.describe(channelname='Name of the channel to be made')
async def createchannel(interaction: discord.Interaction, category: discord.CategoryChannel, channelname: str):
    if ownerID == interaction.user.id:
        channel = await category.create_text_channel(channelname)
        await interaction.response.send_message(f"Created <#{channel.id}> at {getTime()}", ephemeral=True)  # ephemeral means "locally" sent to client.
    else:
        await interaction.response.send_message(f"This is a Protected Command.", ephemeral=True)


@tree.command(guild=discord.Object(id=serverID), name='editmessage', description='Edits a message')
@app_commands.describe(messagelink='The link to the message you would like to edit.')
@app_commands.describe(newmessage='The edits you would like to perform to the message.')
async def editmessage(interaction: discord.Interaction, messagelink: str, newmessage: str):
    if ownerID != interaction.user.id:
        await interaction.response.send_message(f"This is a Protected Command.", ephemeral=True)
        return
    channelid = int(messagelink.split("/")[-2])
    messageid = int(messagelink.split("/")[-1])
    channel = await interaction.client.fetch_channel(channelid)
    message = await channel.fetch_message(messageid)
    await message.edit(content=newmessage.replace("\\n", chr(10)))
    await interaction.response.send_message(f"I might have edited it, it might have errored, no clue lol.", ephemeral=True)


@tree.command(guild=discord.Object(id=serverID), name='cleanmessage', description='Cleans a message')
@app_commands.describe(messagelink='The link to the message you would like to clean.')
async def cleanmessage(interaction: discord.Interaction, messagelink: str):
    if ownerID != interaction.user.id:
        await interaction.response.send_message(f"This is a Protected Command.", ephemeral=True)
        return
    channelid = int(messagelink.split("/")[-2])
    messageid = int(messagelink.split("/")[-1])
    channel = await interaction.client.fetch_channel(channelid)
    message = await channel.fetch_message(messageid)
    cleanedfirstpartofmessagecontent = message.content.split("\n")[0].split(".")[0] + "`"
    cleanedmessage = cleanedfirstpartofmessagecontent + re.sub(r'^.*?\n', ' \n', message.content)
    await message.edit(content=cleanedmessage)
    await interaction.response.send_message(f"I might have edited it, it might have errored, no clue lol.", ephemeral=True)


@tree.command(guild=discord.Object(id=serverID), name='changeperms', description='Enables and Disables Certain Perms')
@app_commands.describe(deleteperms='Delete Perms On/OFF')
@app_commands.describe(viewperms='View Perms On/OFF')
@app_commands.describe(adminperms='Admin Perms On/OFF')
async def changeperms(interaction: discord.Interaction, deleteperms: bool = False, viewperms: bool = False, adminperms: bool = False):
    if ownerID == interaction.user.id:
        await interaction.response.send_message(f"Roles updated at {getTime()}", ephemeral=True)
        DPRID = interaction.guild.get_role(deletePermsRoleID)
        VPRID = interaction.guild.get_role(viewPermsRoleID)
        APRID = interaction.guild.get_role(adminPermsRoleID)
        if deleteperms:
            await interaction.user.add_roles(DPRID)
        else:
            await interaction.user.remove_roles(DPRID)
        if viewperms:
            await interaction.user.add_roles(VPRID)
        else:
            await interaction.user.remove_roles(VPRID)
        if adminperms:
            await interaction.user.add_roles(APRID)
        else:
            await interaction.user.remove_roles(APRID)
    else:
        await interaction.response.send_message(f"This is a Protected Command.", ephemeral=True)


@tree.command(guild=discord.Object(id=serverID), name='updatechannel', description='Updates the default channel temporarily until bot restarts.')
@app_commands.describe(channel='The channel to be chosen for things to be default sent too.')
async def updatechannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if ownerID == interaction.user.id:
        global updatedDefaultChannel
        updatedDefaultChannel = channel.id
        await interaction.response.send_message(f"Updated default channel to <#{channel.id}> at {getTime()}", ephemeral=True)  # ephemeral means "locally" sent to client.
    else:
        await interaction.response.send_message(f"This is a Protected Command.", ephemeral=True)


@tree.command(guild=discord.Object(id=serverID), name='upload', description='Upload Files')  # guild specific slash command
@app_commands.describe(channel='The channel to Send it in.')
@app_commands.describe(filename='Name of the File')
@app_commands.describe(url='Url of the Image')
@app_commands.describe(spoiler='Whether or not the image should be hidden')
@app_commands.describe(source='Sources which may include any text')
async def upload(interaction: discord.Interaction, url: str, filename: str, channel: discord.TextChannel = None, spoiler: bool = False, source: str = None):
    modifiedSource = f"Uploaded file: `{getBasicFileName(filename, url)}`"
    if source is not None:
        modifiedSource = f"{modifiedSource}\n`{source}`"
    await interaction.response.send_message(f"Attempting upload of url for {url} ", ephemeral=True)
    await sendFile(url=url, filename=filename, spoiler=spoiler, channel=channel, source=modifiedSource)


@tree.command(guild=discord.Object(id=serverID), name='directupload', description='Directly replies & uploads Files')  # guild specific slash command
@app_commands.describe(filename='Name of the File')
@app_commands.describe(url='Url of the Image')
@app_commands.describe(spoiler='Whether or not the image should be hidden')
@app_commands.describe(source='Sources which may include any text')
async def upload(interaction: discord.Interaction, url: str, filename: str, spoiler: bool = False, source: str = None):
    modifiedSource = f"Uploaded file: `{getBasicFileName(filename, url)}`"
    if source is not None:
        modifiedSource = f"{modifiedSource}\n`{source}`"
    await interaction.response.send_message(f"Attempting upload of url for {url} ", ephemeral=True)
    await sendFile(url=url, filename=filename, spoiler=spoiler, source=modifiedSource, channel=interaction.channel)


@tree.command(guild=discord.Object(id=serverID), name='avatar', description='Uploads Avatars')  # guild specific slash command
@app_commands.describe(channel='The channel to Send it in.')
@app_commands.describe(userid='ID of the User')
@app_commands.describe(spoiler='Whether or not the image should be hidden')
@app_commands.describe(source='Sources which may include any text')
async def avatar(interaction: discord.Interaction, userid: str, channel: discord.TextChannel = None, spoiler: bool = False, source: str = None):
    try:
        discUser = await client.fetch_user(bot, int(userid))
    except discord.NotFound:
        await interaction.response.send_message(f"User was not found for {userid} ", ephemeral=True)
        return
    if discUser.avatar is None:
        await interaction.response.send_message(f"User has no avatar for `{discUser.id}`", ephemeral=True)
        return
    await interaction.response.send_message(f"Attempting upload of avatar for {userid} ", ephemeral=True)
    await sendAvatar(userID=userid, spoiler=spoiler, channel=channel, source=source)


@tree.command(guild=discord.Object(id=serverID), name='banner', description='Uploads Banners')  # guild specific slash command
@app_commands.describe(channel='The channel to Send it in.')
@app_commands.describe(userid='ID of the User')
@app_commands.describe(spoiler='Whether or not the image should be hidden')
@app_commands.describe(source='Sources which may include any text')
async def banner(interaction: discord.Interaction, userid: str, channel: discord.TextChannel = None, spoiler: bool = False, source: str = None):
    try:
        discUser = await client.fetch_user(bot, int(userid))
    except discord.NotFound:
        await interaction.response.send_message(f"User was not found for {userid} ", ephemeral=True)
        return
    if discUser.banner.url is None:
        await interaction.response.send_message(f"User does not have a banner for {userid} ", ephemeral=True)
        return
    await interaction.response.send_message(f"Attempting upload of banner for {userid} ", ephemeral=True)
    await sendBanner(userID=userid, spoiler=spoiler, channel=channel, source=source)


@tree.command(guild=discord.Object(id=serverID), name='info', description='Replies with info on the users features')  # guild specific slash command
@app_commands.describe(userid='ID of the User')
async def info(interaction: discord.Interaction, userid: str):
    try:
        discUser = await client.fetch_user(bot, int(userid))
    except discord.NotFound:
        await interaction.response.send_message(f"User was not found for {userid} ", ephemeral=True)
        return
    if discUser.avatar is None:
        await interaction.response.send_message(f"User has no avatar for `{discUser.id}`", ephemeral=True)
        return
    if discUser.banner is None:
        userAvatarURL = discUser.avatar.url
        await interaction.response.send_message(f"Showing Avatar of `{discUser.name}#{discUser.discriminator}`| {discUser.mention} | `{discUser.id}`\n{userAvatarURL}", ephemeral=True, view=infoAvatar(discUser.id))  # ephemeral means "locally" sent to client.
    else:
        userAvatarURL = discUser.avatar.url
        userBannerURL = adjustPictureSizeDiscord(discUser.banner.url, 1024)

        await interaction.response.send_message(f"Showing Avatar & Banner of `{discUser.name}#{discUser.discriminator}`| {discUser.mention} | `{discUser.id}`\n{userAvatarURL}\n{userBannerURL}", ephemeral=True, view=infoAvatarAndBanner(discUser.id))  # ephemeral means "locally" sent to client.


class infoAvatarAndBanner(discord.ui.View):
    def __init__(self, userID):
        super().__init__()
        self.userID = userID

    @discord.ui.button(label='Avatar', style=discord.ButtonStyle.primary)
    async def avatar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f'Sending Avatar for {self.userID}', ephemeral=True)
        await sendAvatar(userID=self.userID, channel=None, spoiler=False, source=None)

    @discord.ui.button(label='Banner', style=discord.ButtonStyle.success)
    async def banner(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f'Sending Banner for {self.userID}', ephemeral=True)
        await sendBanner(userID=self.userID, channel=None, spoiler=False, source=None)

    @discord.ui.button(label='Hash', style=discord.ButtonStyle.secondary)
    async def hash(self, interaction: discord.Interaction, button: discord.ui.Button):
        discUser = await client.fetch_user(bot, int(self.userID))
        returnedBytesAvatar = await getBytesOfURL(discUser.avatar.url)
        returnedBytesBanner = await getBytesOfURL(adjustPictureSizeDiscord(discUser.banner.url, 1024))
        await interaction.response.send_message(f'Attached Hash for {self.userID}\nAvatar: `{getHashOfBytes(returnedBytesAvatar.content)}`\nBanner: `{getHashOfBytes(returnedBytesBanner.content)}`', ephemeral=True)


class infoAvatar(discord.ui.View):
    def __init__(self, userID):
        super().__init__()
        self.userID = userID

    @discord.ui.button(label='Avatar', style=discord.ButtonStyle.primary)
    async def avatar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f'Sending Avatar {self.userID}', ephemeral=True)
        await sendAvatar(userID=self.userID, channel=None, spoiler=False, source=None)

    @discord.ui.button(label='Hash', style=discord.ButtonStyle.secondary)
    async def hash(self, interaction: discord.Interaction, button: discord.ui.Button):
        discUser = await client.fetch_user(bot, int(self.userID))
        returnedBytes = await getBytesOfURL(discUser.avatar.url)
        await interaction.response.send_message(f'Attached Hash for {self.userID}\nAvatar: `{getHashOfBytes(returnedBytes.content)}`', ephemeral=True)


async def sendAvatar(userID, channel, spoiler, source):
    discUser = await client.fetch_user(bot, int(userID))
    userAvatarURL = discUser.avatar.url
    modifiedSource = f"Uploaded Avatar of `{discUser.name}#{discUser.discriminator}`| {discUser.mention} | `{discUser.id}`"
    if source is not None:
        modifiedSource = f"{modifiedSource}\n`{source}`"
    await sendFile(url=userAvatarURL, filename=discUser.id, channel=channel, spoiler=spoiler, source=modifiedSource)


async def sendBanner(userID, channel, spoiler, source):
    discUser = await client.fetch_user(bot, int(userID))
    userBannerURL = adjustPictureSizeDiscord(discUser.banner.url, 1024)
    modifiedSource = f"Uploaded Banner of `{discUser.name}#{discUser.discriminator}`| {discUser.mention} | `{discUser.id}`"
    if source is not None:
        modifiedSource = f"{modifiedSource}\n`{source}`"
    await sendFile(url=userBannerURL, filename=discUser.id, channel=channel, spoiler=spoiler, source=modifiedSource)


async def sendFile(url, filename, channel, spoiler, source):
    returnedBytes = await getBytesOfURL(url)
    if checkFileSize(returnedBytes):
        finalFileName = getFileName(filename=filename, RB=returnedBytes, spoiler=spoiler, url=url)
        fileToSend = discord.File(io.BytesIO(returnedBytes.content), filename=finalFileName)
        if channel is None:
            channel = getDefaultChannel()
        await channel.send(f"{source}\nOrigin URL: `{url}`\nHash: `{getHashOfBytes(returnedBytes.content)}` Size: `{getFileSize(returnedBytes.content)}`", file=fileToSend)
    else:
        if channel is None:
            channel = getDefaultChannel()
        if not source.startswith("Uploaded "):
            source = f"Failed Uploading file at: {url}\n + {source}"
        await channel.send(f"{source}\nOrigin URL: `{url}`\nHash: `{getHashOfBytes(returnedBytes.content)}` Size: `{getFileSize(returnedBytes.content)}`")


bot.run(getBotKey())
