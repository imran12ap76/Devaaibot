import math
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.ia_filterdb import get_search_counts, get_search_results
from plugins.pm_filter import manual_filters
from utils import get_size

@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    if not await manual_filters(client, message):
        return
    await group_post_filter(client, message)

async def group_post_filter(client, message):
    text = message.text
    count = await get_search_counts(text)
    if not count:
        return
    new_message = f"<b>Title : #{text.replace(' ', '_')}\nTotal Files : {count}\n\n© Tamilgram"
    await message.reply_text(new_message, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Download', url=f"https://t.me/{client.me.username}?start=pquery_{message.id}_{message.chat.id}")]]))
    
async def post_filter(client, message):
    command = message.command[1]
    _, msg_id, chat_id = command.split('_', 2)
    og_msg = await client.get_messages(int(chat_id), int(msg_id))
    text = og_msg.text
    files, offset, total_results = await get_search_results(text, max_results=6)
    if not files:
        return
    movie_text = f'<i>Hey {message.from_user.mention}\n\nHere are the results that i found for your query "{text}" 👇</i>'
    for file in files:
        movie_text += f"➡️ <a href='https://t.me/{client.me.username}?start=file_{file.file_id}'>{file.file_name}</a> {get_size(file.file_size)}\n\n"
    btns = []
    if offset != "":
        btn.append(
            [InlineKeyboardButton(text=f"❄️ ᴩᴀɢᴇꜱ 1/{math.ceil(int(total_results) / 6)}", callback_data="pages"),
            InlineKeyboardButton(text="ɴᴇxᴛ ➡️", callback_data=f"pmnext_{offset}_{msg_id}_{chat_id}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="❄️ ᴩᴀɢᴇꜱ 1/1", callback_data="pages")]
        )
    await message.reply_text(movie_text, reply_markup=InlineKeyboardMarkup(btns))

@Client.on_callback_query(filters.regex('^pmnext'))
async def pm_next_page(bot, query):
    _, offset, msg_id, chat_id = query.data.split('_')
    try: offset = int(off_set)
    except: offset = 0
    og_msg = await client.get_messages(int(chat_id), int(msg_id))
    text = og_msg.text
    files, next_offset, total_results = await get_search_results(text, max_results=6, offset=offset)
    if not files:
        await query.message.delete()
        return await query.answer("Something Wrong, Try Again", show_alert=True)
    movie_text = f'<i>Hey {message.from_user.mention}\n\nHere are the results that i found for your query "{text}" 👇</i>'
    for file in files:
        movie_text += f"➡️ <a href='https://t.me/{client.me.username}?start=file_{file.file_id}'>{file.file_name}</a> {get_size(file.file_size)}\n\n"
    btns = []
    if 0 < offset <= 6: off_set = 0
    elif offset == 0: off_set = None
    else: off_set = offset - 6
    if next_offset == 0:
        btn.append(
            [InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data=f"pmnext_{off_set}_{msg_id}_{chat_id}"),
             InlineKeyboardButton(f"❄️ ᴩᴀɢᴇꜱ {math.ceil(int(offset) / 6) + 1} / {math.ceil(total / 6)}", callback_data="pages")]                                  
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"❄️ {math.ceil(int(offset) / 6) + 1} / {math.ceil(total / 6)}", callback_data="pages"),
             InlineKeyboardButton("ɴᴇxᴛ ➡️", callback_data=f"pmnext_{next_offset}_{msg_id}_{chat_id}")])
    else:
        btn.append([
            InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data=f"pmnext_{off_set}_{msg_id}_{chat_id}"),
            InlineKeyboardButton(f"❄️ {math.ceil(int(offset) / 6) + 1} / {math.ceil(total / 6)}", callback_data="pages"),
            InlineKeyboardButton("ɴᴇxᴛ ➡️", callback_data=f"pmnext_{next_offset}_{msg_id}_{chat_id}")
        ])
    try:
        await query.message.edit(text=movie_text, reply_markup=InlineKeyboardMarkup(btns))
    except MessageNotModified:
        pass
    await query.answer()