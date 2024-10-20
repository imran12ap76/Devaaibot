import asyncio
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Script import script
from info import LOG_CHANNEL, NO_RESULTS_MSG
from utils import get_poster, SPELL_CHECK
import logging
import re


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def advantage_spell_chok(client, msg):
    mv_id = msg.id
    mp = msg
    mv_rqst = msg.text
    reqstr1 = msg.from_user.id if msg.from_user else 0

    # Clean the query by removing common words
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", mv_rqst, flags=re.IGNORECASE
    )  # please contribute some common words to filter
    query = query.strip() + " movie"

    try:
        movies = await get_poster(mv_rqst, bulk=True)
    except Exception as e:
        logger.exception(e)
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
            InlineKeyboardButton("Gá´á´É¢ÊŸá´‡", url=f"https://www.google.com/search?q={reqst_gle}+movie")
        ]]
        if NO_RESULTS_MSG:
            await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr1, msg.from_user.mention, mv_rqst)))
        k = await msg.reply_text(
            text=script.I_CUDNT.format(mv_rqst),
            reply_markup=InlineKeyboardMarkup(button)
        )
        await asyncio.sleep(30)
        await k.delete()
        await mp.delete()
        return

    movielist = []
    if not movies:
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
            InlineKeyboardButton("Gá´á´É¢ÊŸá´‡", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        if NO_RESULTS_MSG:
            await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr1, msg.from_user.mention, mv_rqst)))
        k = await msg.reply_text(
            text=script.I_CUDNT.format(mv_rqst),
            reply_markup=InlineKeyboardMarkup(button)
        )
        await asyncio.sleep(30)
        await k.delete()
        await mp.delete()
        return

    movielist += [movie.get('title') for movie in movies]
    movielist += [f"{movie.get('title')} {movie.get('year')}" for movie in movies]
    SPELL_CHECK[mv_id] = movielist

    btn = [
        [
            InlineKeyboardButton(
                text=movie_name.strip(),
                callback_data=f"spol#{reqstr1}#{k}",
            )
        ]
        for k, movie_name in enumerate(movielist)
    ]
    btn.append([InlineKeyboardButton(text="Close", callback_data=f'spol#{reqstr1}#close_spellcheck')])

    spell_check_del = await msg.reply_text(
        text=script.CUDNT_FND.format(mv_rqst),
        reply_markup=InlineKeyboardMarkup(btn)
    )

    await asyncio.sleep(60)
    await spell_check_del.delete()
