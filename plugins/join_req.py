import logging
from pyrogram import Client, filters, enums
from pyrogram import Client as client
from pyrogram.types import ChatJoinRequest, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MediaEmpty  # Error handling ke liye specific import
from database.join_reqs import JoinReqs
from database.ia_filterdb import get_file_details
from info import ADMINS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION, CHNL_LNK, GRP_LNK, REQ_CHANNEL1, REQ_CHANNEL2, REQ_CHANNEL3
from utils import global_rsub, get_size, temp_files

db = JoinReqs

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

@Client.on_chat_join_request(filters.chat(REQ_CHANNEL1) | 
                          filters.chat(REQ_CHANNEL2) | 
                          filters.chat(REQ_CHANNEL3))
async def join_reqs(client: Client, join_req: ChatJoinRequest):
    chat_id = join_req.chat.id
    logger.info("recieved rquest", chat_id)
    chats = [REQ_CHANNEL1, REQ_CHANNEL2, REQ_CHANNEL3]

    if chat_id in chats:
        user_id = join_req.from_user.id

        if user_id in global_rsub:
            channels = global_rsub[user_id]

            if chat_id not in channels:
                await send_file(client, user_id, file_id)
                channels.append(chat_id)
                global_rsub[user_id] = channels


async def send_file(client: Client, user_id: int, file_id: str) -> None:
    files = await get_file_details(file_id)
    
    if not files:
        logger.error("Error: File details not found for file_id: %s", file_id)
        return

    file = files[0]
    title = file.file_name
    size = get_size(file.file_size)
    
    f_caption = file.file_name
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption = CUSTOM_FILE_CAPTION.format(
                file_name=file.file_name,
                file_size=size,
                file_caption=file.file_name or "No caption available."
            )
        except Exception as e:
            logger.exception("Error formatting custom caption: %s", e)
    
    if not file.file_size or file.file_size <= 0:
        logger.error("Error: File size is empty or invalid for file_id: %s", file_id)
        return

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
                    ],
                    [
                        InlineKeyboardButton("Bᴏᴛ Oᴡɴᴇʀ", url="t.me/Joyboy_Nikkaman")
                    ]
                ]
            )
        )
        logger.info("File sent successfully to user_id: %s", user_id)
    except MediaEmpty:
        logger.error("Error: The media file is empty or invalid for file_id: %s", file_id)
        # Optionally notify the user
        await client.send_message(user_id, "Sorry, the file is empty or invalid.")
    except Exception as e:
        logger.exception("Failed to send file to user_id: %s: %s", user_id, e)
        await client.send_message(user_id, "An error occurred while sending the file.")
