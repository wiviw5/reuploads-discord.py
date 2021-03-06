import httpx


def getFileExtensionType(fileBytes, url):
    if fileBytes.startswith(bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])):
        return '.png'
    if fileBytes.startswith(bytes([0xFF, 0xD8, 0xFF, 0xE1])):
        return '.jpg'
    if fileBytes.startswith(bytes([0xFF, 0xD8, 0xFF, 0xE0])):
        return '.jpg'
    if fileBytes.startswith(bytes([0x47, 0x49, 0x46, 0x38])):
        return '.gif'
    if fileBytes.startswith(bytes([0x52, 0x49, 0x46, 0x46])):
        return '.webp'
    if fileBytes.startswith(bytes([0x00, 0x00, 0x00, 0x20, 0x66, 0x74, 0x79, 0x70])):
        return '.mp4'
    if fileBytes.startswith(bytes([0x00, 0x00, 0x00, 0x1c, 0x66, 0x74, 0x79, 0x70])):
        return '.mp4'
    if fileBytes.startswith(bytes([0x00, 0x00, 0x00, 0x14, 0x66, 0x74, 0x79, 0x70])):
        return '.mov'
    else:
        ext = url.split(".")[-1].split("?")[0]
        return f"{ext}_reportthis_.txt"


# Returns true if the size of the file is under discords upload threshold for default servers
def checkFileSize(Bytes):
    return len(Bytes.content) <= 8388608


def translateBytesIntoKB(incomingBytes):
    return incomingBytes / 1024


def translateBytesIntoMB(incomingBytes):
    return incomingBytes / 1048576


# def getFileExtensionType(fileBytes):
#    for ext in magicNumbers:
#        if fileBytes.startswith(magicNumbers[ext]):
#            return ext


def getFileName(filename, RB, spoiler, url):
    if spoiler:
        return f"SPOILER_{filename}{getFileExtensionType(RB.content, url)}"
    else:
        return f"{filename}{getFileExtensionType(RB.content, url)}"


def getFileSize(RB):
    ByteValue = len(RB)
    if ByteValue <= 1024:
        return f"{ByteValue} Bytes"
    elif ByteValue <= 1048576:
        return f"{'%.2f' % translateBytesIntoKB(ByteValue)} KB"
    else:
        return f"{'%.2f' % translateBytesIntoMB(ByteValue)} MB"


async def getBytesOfURL(url):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        return r
