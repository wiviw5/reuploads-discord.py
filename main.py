import io
import discord
from discord import app_commands
from utils import getTime, getBotKey, checkAndSetupConfigFile, getMainGuildID, getDefaultChannelID, getDeletePermsRoleID, getViewPermsRoleID, getAdminPermsRoleID, getOwnerID
from filesutils import getBytesOfURL, checkFileSize, getFileSize, getFileName

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
ownerID = int(getOwnerID())


def getDefaultChannel():
    return bot.get_channel(int(defaultChannelID))


def getAttemptedUploadMessage(filename, url):
    return f"Attempted Upload of `{filename}` at `{getTime()}` \n{url}"


def getAttemptedUploadMessageWithSource(filename, url, source):
    return f"Attempted Upload of `{filename}` at `{getTime()}` \n{url}\nSource: `{source}`"


def getSuccessfulUploadMessage(returnedBytes):
    return f"Completed File Download Successfully at {getTime()}, Uploading {getFileSize(returnedBytes.content)} of content."


def getUnsuccessfulUploadMessage(returnedBytes):
    return f"Completed File Download Successfully at {getTime()}, Unable to upload {getFileSize(returnedBytes.content)} of content."


@tree.command(guild=discord.Object(id=serverID), name='createchannel', description='Creates a Channel')
@app_commands.describe(category='The category to create it in.')
@app_commands.describe(channelname='Name of the channel to be made')
async def createchannel(interaction: discord.Interaction, category: discord.CategoryChannel, channelname: str):
    if ownerID == interaction.user.id:
        channel = await category.create_text_channel(channelname)
        await interaction.response.send_message(f"Created <#{channel.id}> at {getTime()}", ephemeral=True)  # ephemeral means "locally" sent to client.
    else:
        await interaction.response.send_message(f"This is a Protected Command.", ephemeral=True)


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


@tree.command(guild=discord.Object(id=serverID), name='upload', description='Upload Files')  # guild specific slash command
@app_commands.describe(channel='The channel to Send it in.')
@app_commands.describe(filename='Name of the File')
@app_commands.describe(url='Url of the Image')
@app_commands.describe(source='Url of the Source')
async def upload(interaction: discord.Interaction, url: str, filename: str, spoiler: bool = False, channel: discord.TextChannel = None, source: str = None):
    returnedBytes = await getBytesOfURL(url)
    if channel is None:
        channel = getDefaultChannel()
    if source is None:
        if checkFileSize(returnedBytes):
            await interaction.response.send_message(getSuccessfulUploadMessage(returnedBytes), ephemeral=True)  # ephemeral means "locally" sent to client.
            await channel.send(f"Uploaded `{filename}` at `{getTime()}` \n`{url}`", file=discord.File(io.BytesIO(returnedBytes.content), filename=getFileName(filename, returnedBytes, spoiler, url)))
        else:
            await interaction.response.send_message(getUnsuccessfulUploadMessage(returnedBytes), ephemeral=True)
            await channel.send(getAttemptedUploadMessage(filename, url))
    else:
        if checkFileSize(returnedBytes):
            await interaction.response.send_message(getSuccessfulUploadMessage(returnedBytes), ephemeral=True)  # ephemeral means "locally" sent to client.
            await channel.send(f"Uploaded `{filename}` at `{getTime()}` \n`{url}`\nSource: `{source}`", file=discord.File(io.BytesIO(returnedBytes.content), filename=getFileName(filename, returnedBytes, spoiler, url)))
        else:
            await interaction.response.send_message(getUnsuccessfulUploadMessage(returnedBytes), ephemeral=True)
            await channel.send(getAttemptedUploadMessageWithSource(filename, url, source))


@tree.command(guild=discord.Object(id=serverID), name='avatar', description='Uploads Avatars')  # guild specific slash command
@app_commands.describe(channel='The channel to Send it in.')
@app_commands.describe(userid='ID of the User')
async def avatar(interaction: discord.Interaction, userid: str, spoiler: bool = False, channel: discord.TextChannel = None):
    discUser = await client.fetch_user(bot, userid)
    userAvatarURL = discUser.avatar.url
    returnedBytes = await getBytesOfURL(userAvatarURL)
    if channel is None:
        channel = getDefaultChannel()
    if checkFileSize(returnedBytes):
        await interaction.response.send_message(getSuccessfulUploadMessage(returnedBytes), ephemeral=True)  # ephemeral means "locally" sent to client.
        await channel.send(f"Uploaded `{discUser.name}` | `{discUser.id}` | <@{discUser.id}> at `{getTime()}` \n`{userAvatarURL}`", file=discord.File(io.BytesIO(returnedBytes.content), filename=getFileName(discUser.name, returnedBytes, spoiler, userAvatarURL)))
    else:
        await interaction.response.send_message(getUnsuccessfulUploadMessage(returnedBytes), ephemeral=True)
        await channel.send((getAttemptedUploadMessage(discUser.name, userAvatarURL)))


@tree.command(guild=discord.Object(id=serverID), name='banner', description='Uploads Banners')  # guild specific slash command
@app_commands.describe(channel='The channel to Send it in.')
@app_commands.describe(userid='ID of the User')
async def banner(interaction: discord.Interaction, userid: str, spoiler: bool = False, channel: discord.TextChannel = None):
    discUser = await client.fetch_user(bot, userid)
    userBannerURL = discUser.banner.url
    returnedBytes = await getBytesOfURL(userBannerURL)
    if channel is None:
        channel = getDefaultChannel()
    if checkFileSize(returnedBytes):
        await interaction.response.send_message(getSuccessfulUploadMessage(returnedBytes), ephemeral=True)  # ephemeral means "locally" sent to client.
        await channel.send(f"Uploaded `{discUser.name}` | `{discUser.id}` | <@{discUser.id}> at `{getTime()}` \n`{userBannerURL}`", file=discord.File(io.BytesIO(returnedBytes.content), filename=getFileName(discUser.name, returnedBytes, spoiler, userBannerURL)))
    else:
        await interaction.response.send_message(getUnsuccessfulUploadMessage(returnedBytes), ephemeral=True)
        await channel.send((getAttemptedUploadMessage(discUser.name, userBannerURL)))


@tree.command(guild=discord.Object(id=serverID), name='info', description='Replies with info on the users features')  # guild specific slash command
@app_commands.describe(userid='ID of the User')
@app_commands.describe(banner='If the banner should be included as well.')
async def banner(interaction: discord.Interaction, userid: str, banner: bool = None):
    discUser = await client.fetch_user(bot, userid)
    if banner is True:
        userAvatarURL = discUser.avatar.url
        userBannerURL = discUser.banner.url
        await interaction.response.send_message(f"Showing Profile: `{discUser.name}` | `{discUser.id}` | <@{discUser.id}> at `{getTime()}` \n{userAvatarURL}\n {userBannerURL}", ephemeral=True)  # ephemeral means "locally" sent to client.
    else:
        userAvatarURL = discUser.avatar.url
        await interaction.response.send_message(f"Showing Profile: `{discUser.name}` | `{discUser.id}` | <@{discUser.id}> at `{getTime()}` \n{userAvatarURL}", ephemeral=True)  # ephemeral means "locally" sent to client.


bot.run(getBotKey())
