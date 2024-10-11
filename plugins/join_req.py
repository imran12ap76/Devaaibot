from logging import getLogger
from pyrogram import Client, filters, enums
from pyrogram.types import ChatJoinRequest, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MediaEmpty  # Error handling ke liye specific import
from database.join_reqs import JoinReqs
from database.ia_filterdb import get_file_details
from info import ADMINS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION, CHNL_LNK, GRP_LNK, REQ_CHANNEL1, REQ_CHANNEL2, REQ_CHANNEL3
from utils import global_rsub, get_size, temp_files

db = JoinReqs
logger = getLogger(__name__) 

@Client.on_chat_join_request()
async def join_reqs(client, join_req: ChatJoinRequest):
    chat_id = join_req.chat.id
    chats = [REQ_CHANNEL1, REQ_CHANNEL2, REQ_CHANNEL3]
    if chat_id in chats:
        user_id = join_req.from_user.id
        if user_id in global_rsub:
            channels = global_rsub[user_id]
            if chat_id not in channels:
                if user_id in temp_files:
                    file_id = temp_files[user_id]
                    await send_file(client, user_id, file_id)
                    del temp_files[user_id]
                
                channels.append(chat_id)
                global_rsub[user_id] = channels

async def send_file(client, user_id, file_id):
    files = await get_file_details(file_id)
    if not files:
        print("Error: File details not found.")
        return

    file = files[0]
    title = file.file_name
    size = get_size(file.file_size)
    
    f_caption = file.file_name
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption = CUSTOM_FILE_CAPTION.format(
                file_name=file.file_name, file_size=get_size(file.file_size), file_caption=file.file_name
            )
        except Exception as e:
            logger.exception(e)
           
    try:
        m = await client.send_cached_media(
            chat_id=user_id,
            file_id=file_id,
            caption=f_caption,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=GRP_LNK),
                        InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
                    ],[
                        InlineKeyboardButton("Bᴏᴛ Oᴡɴᴇʀ", url="t.me/Joyboy_Nikkaman")
                    ]
                ]
            )
        )
    except MediaEmpty:
        print("Error: The media file is empty or invalid.")
        return
