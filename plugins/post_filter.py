import math
import asyncio
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageNotModified
from database.ia_filterdb import get_search_counts, get_search_results
from plugins.pm_filter import manual_filters, global_filters
from plugins.helper.spell_chk import advantage_spell_chok
from utils import get_size, SPELL_CHECK
from info import NO_RESULTS_MSG, LOG_CHANNEL
from Script import script
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    if await manual_filters(client, message):
        return
    await group_post_filter(client, message)

@Client.on_message(filters.private & filters.text & filters.incoming)
async def givepvt_filter(bot, message):
    if await manual_filters(bot, message):
        return
    await pvt_group_post_filter(bot, message)
    
async def group_post_filter(client, message):
    text = message.text
    count = await get_search_counts(text)
    if not count:
        return await advantage_spell_chok(client, message)
    new_message = f"<b>Title : #{text.replace(' ', '_')}\nTotal Files : {count}\n\n© @Spidy_Updates</b>"
    await message.reply_text(new_message, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Download', url=f"https://t.me/{client.me.username}?start=pquery_{message.id}_{message.chat.id}")]]))

async def pvt_group_post_filter(bot, message):
    text = message.text
    count = await get_search_counts(text)
    if not count:
        return
    new_message = f"<b>Title : #{text.replace(' ', '_')}\nTotal Files : {count}\n\n© @Spidy_Updates</b>"
    await message.reply_text(new_message, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Download', url=f"https://t.me/{bot.me.username}?start=pquery_{message.id}_{message.chat.id}")]]))
    
@Client.on_callback_query(filters.regex(r"postnext"), group=-1)
async def pm_post_next_page(bot, query):
    _, offset, msg_id, chat_id, is_spol = query.data.split('_')
    is_spol = is_spol.lower() == 'true'
    try: offset = int(offset)
    except: offset = 0
    if is_spol:
        movies = SPELL_CHECK.get(int(chat_id))
        if not movies:
            return await query.message.delete()
        movie = movies[(int(chat_id))]
        movie = re.sub(r"[:\-]", " ", movie)
        text = re.sub(r"\s+", " ", movie).strip()
    else:
        og_msg = await bot.get_messages(int(chat_id), int(msg_id))
        text = og_msg.text
    files, next_offset, total_results = await get_search_results(text, max_results=6, offset=offset)
    if not files:
        await query.message.delete()
        return await query.answer("Something Wrong, Try Again", show_alert=True)
    movie_text = f'<i>Hey {query.from_user.mention}\n\nHere are the results that i found for your query "{text}" 👇</i>'
    btns = []
    for file in files:
        btns.append([InlineKeyboardButton(file.file_name, url=f"https://t.me/{bot.me.username}?start=file_{file.file_id}")])
    if 0 < offset <= 6:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 6
    if next_offset == 0:
        btns.append(
            [InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data=f"postnext_{off_set}_{msg_id}_{chat_id}_{is_spol}"),
            InlineKeyboardButton(f"❄️ ᴩᴀɢᴇꜱ {math.ceil(int(offset) / 6) + 1} / {math.ceil(total_results / 6)}", callback_data="pages")]                                  
        )
    elif off_set is None:
        btns.append(
            [InlineKeyboardButton(f"❄️ {math.ceil(int(offset) / 6) + 1} / {math.ceil(total_results / 6)}", callback_data="pages"),
            InlineKeyboardButton("ɴᴇxᴛ ➡️", callback_data=f"postnext_{next_offset}_{msg_id}_{chat_id}_{is_spol}")])
    else:
        btns.append([
            InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data=f"postnext_{off_set}_{msg_id}_{chat_id}_{is_spol}"),
            InlineKeyboardButton(f"❄️ {math.ceil(int(offset) / 6) + 1} / {math.ceil(total_results / 6)}", callback_data="pages"),
            InlineKeyboardButton("ɴᴇxᴛ ➡️", callback_data=f"postnext_{next_offset}_{msg_id}_{chat_id}_{is_spol}")
        ])
    try:
        await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(btns))
    except MessageNotModified:
        pass
    await query.answer()

async def post_filter(client, message, is_spol=False):
    command = message.command[1]
    chat_id, msg_id = None, None
    if is_spol:
        await message.react(emoji="🔥")
        _, r_user_id, r_k_id = command.split('_', 2)
        movies = SPELL_CHECK.get(int(r_user_id))
        if not movies:
            return await message.reply_text(script.OLD_ALRT_TXT.format(message.from_user.first_name))
        if int(r_user_id) != 0 and message.from_user.id != int(r_user_id):
            return await message.reply_text(script.ALRT_TXT.format(message.from_user.first_name))
        movie = movies[(int(r_k_id))]
        movie = re.sub(r"[:\-]", " ", movie)
        text = re.sub(r"\s+", " ", movie).strip()
        files, offset, total_results = await get_search_results(text, max_results=6)
        if not files:
            return await message.reply_text("No Files Found")
    else:
        _, msg_id, chat_id = command.split('_', 2)
        og_msg = await client.get_messages(int(chat_id), int(msg_id))
        text = og_msg.text
        files, offset, total_results = await get_search_results(text, max_results=6)
        if not files:
            return await advantage_spell_chok(client, message)
    movie_text = f'<i>Hey {message.from_user.mention}\n\nHere are the results that i found for your query "{text}" 👇</i>'
    btns = []
    for file in files:
        btns.append([InlineKeyboardButton(file.file_name, url=f"https://t.me/{client.me.username}?start=file_{file.file_id}")])
    if offset != "":
        btns.append(
            [InlineKeyboardButton(text=f"❄️ ᴩᴀɢᴇꜱ 1/{math.ceil(int(total_results) / 6)}", callback_data="pages"),
            InlineKeyboardButton(text="ɴᴇxᴛ ➡️", callback_data=f"postnext_{offset}_{msg_id if msg_id else 0}_{chat_id if chat_id else r_user_id}_{is_spol}")]
        )
    else:
        btns.append(
            [InlineKeyboardButton(text="❄️ ᴩᴀɢᴇꜱ 1/1", callback_data="pages")]
        )
    await message.reply_text(movie_text, reply_markup=InlineKeyboardMarkup(btns))

@Client.on_callback_query(filters.regex(r"^spol"), group=-1)
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    elif int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    movie = movies[(int(movie_))]
    movie = re.sub(r"[:\-]", " ", movie)
    movie = re.sub(r"\s+", " ", movie).strip()
    await query.answer(script.TOP_ALRT_MSG)
    if await global_filters(bot, query.message, text=movie):
        return
    elif await manual_filters(bot, query.message, text=movie):
        return
    files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
    if files:
        k = (movie, files, offset, total_results)
        await post_filter(bot, query.message, k)
    else:
        reqstr1 = query.from_user.id if query.from_user else 0
        if NO_RESULTS_MSG:
            await bot.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, query.from_user.mention, movie)))
        k = await query.message.edit(script.MVE_NT_FND)
        await asyncio.sleep(10)
        await k.delete()
