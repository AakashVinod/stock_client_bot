from telegram import Bot

async def generate_one_time_invite(bot: Bot, chat_id: str):
    try:
        invite = await bot.create_chat_invite_link(
            chat_id=chat_id,
            member_limit=1,
            creates_join_request=False,
            expire_date=None
        )
        return invite.invite_link
    except Exception as e:
        print(f"⚠️ Error generating invite link: {e}")
        return None
