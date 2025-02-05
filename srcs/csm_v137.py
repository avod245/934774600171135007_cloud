import discord
from discord.ext import commands, tasks
from discord import app_commands, ui, File, ButtonStyle
from typing import Optional
import aiosqlite
import datetime
import json

import docker

import re
import uuid
import random
import string

import shutil, os

# /list_sub & /add_sub fonctionnal
# Time options selection added
# + /modify_sub added
# FULL EN
# Bot selection Added
# Loop alerts fixed
# Message Embed of Ended sub Added
# Sub start Embed Message Added
# Multi-bot Selection Added
# /check_sub Added
# 24h before Sub Expiration Alert Added
# Be sure the Sub Expiration Alert is sent
# ML Sub. Exclusion added in DM Embeds
# Alert Mess Loop Fixed FINNALLY

# /list_subs Enhanced + expired users Added

# Docker managment Added
# /check_all_keys Added
# /my_bots Added
# Multi - bot support /per user
# /setup_bot Fixed w/ bot choice added
# /stop_bt Enhanced w/ bot choice
# auto-role Added
# ML Sub Removed
# /activate Fixed
# /create_key Enhanced
# /create_key Fixed
# /activate Fixed
# /setup_bot Fixed

# FIX COPY FILES
# FINNALLY FIXED !!!!!!!!!!! // last error = 2025-02-05 19:48:36 Config file not found!
# Config file copy & deployment Fixed !!
# Cog load Fixed
# /stop_bot Fixed
# /restart_bot Added

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

sub_logs = 1243480251367948309
clients_subs = 1241037018147061862
clients_cmd = 1272930852061446164

GUILD_ID = 1269818132478955573 # AREA

ADMIN_CHANNEL_ID = sub_logs  # AV CLIENT SUBS 2

time_format = '`%d/%m/%Y`｜`%H:%M`'

# Embed Details / Medias
embed_image_link="https://cdn.discordapp.com/attachments/1125752520229273630/1227797051794919424/rainbow-border.gif?ex=6629b61c&is=6617411c&hm=6f8c594ba125f15c7fd1dfbf34c2d438f2fc901b161075dd341656dfdf9d620b&"
#         embed.set_image(url=embed_image_link)
footer_name="ΛV™" # AV
footer_icon_link="https://cdn.discordapp.com/attachments/1125752520229273630/1258853803495526450/AV_LOGO_V3.png?ex=66bafeb7&is=66b9ad37&hm=bc64bb5c87e0a9cf402be865b893d8e0ad41489c03a40b3f5481b69b35cac3cb&" # AV LOGO 

renewal_url = "https://discord.com/channels/1162142435711918121/1171575828300185611"

support_url = "https://discord.com/channels/1162142435711918121/1171575828300185611"

guide_url = "https://av0.gitbook.io/lv"

on_emoji = "<:on_icon_av_v1:1270039830335590491>"
off_emoji = "<:off_icon_av_v1:1270039815177633905>"


# Time durations in seconds for each time unit
TIME_MULTIPLIERS = {
    "Minute": 60,
    "Hour": 3600,
    "Day": 86400,
    "Week": 604800,
    "Month": 2592000  # Approximation for a month (30 days)
}

diff_durations = [
    app_commands.Choice(name="Minute", value="Minute"),
    app_commands.Choice(name="Hour", value="Hour"),
    app_commands.Choice(name="Day", value="Day"),
    app_commands.Choice(name="Week", value="Week"),
    app_commands.Choice(name="Month", value="Month"),
]

# List of available bots

BOT_SOURCE_MAP = {
    "paypal_bot": "def_bot_srcs/paypal_bot",
    "cashapp_bot": "def_bot_srcs/cashapp_bot",
    "prodigen_bot": "def_bot_srcs/prodigen_bot",
    "vouch_bot": "def_bot_srcs/vouch_bot",
    "stickit_bot": "def_bot_srcs/stickit_bot",
    "slotmachine_bot": "def_bot_srcs/slotmachine_bot",
    "invoice_bot": "def_bot_srcs/invoice_bot",
    "keyauth_bot": "def_bot_srcs/keyauth_bot",
    "sellauth_bot": "def_bot_srcs/sellauth_bot",
    "satochi_bot": "def_bot_srcs/satochi_bot",
    "slot_bot": "def_bot_srcs/slot_bot",
    "ezpanel_bot": "def_bot_srcs/ezpanel_bot",
}

ROLE_MAP = {
    "paypal_bot": 1269825104603385957,
    "cashapp_bot": 1269825150346465411,
    "prodigen_bot": 1269824645956112506,
    "vouch_bot": 1269825240096313355,
    "stickit_bot": 1270031418327695508,
    "slotmachine_bot": 1269825431947972618,
    "invoice_bot": 1269980344485019700,
    "keyauth_bot": 1269978533644468254,
    "sellauth_bot": 1330405507722248212,
    "satochi_bot": 1332168955053473905,
    "slot_bot": 1332169730009600000,
    "ezpanel_bot": 1332170086944997506,
}

AVAILABLE_BOTS = [
    app_commands.Choice(name="PayPal Bot",         value="paypal_bot"),
    app_commands.Choice(name="CashApp Bot",        value="cashapp_bot"),
    app_commands.Choice(name="ProdiGen Bot",       value="prodigen_bot"),
    app_commands.Choice(name="Vouch Bot",          value="vouch_bot"),
    app_commands.Choice(name="Stick-it Bot",       value="stickit_bot"),
    app_commands.Choice(name="Slot Machine Bot",   value="slotmachine_bot"),
    app_commands.Choice(name="Invoice Bot",        value="invoice_bot"),
    app_commands.Choice(name="KeyAuth Bot",        value="keyauth_bot"),
    app_commands.Choice(name="SellAuth Bot",       value="sellauth_bot"),
    app_commands.Choice(name="Satochi Crypto Bot", value="satochi_bot"),
    app_commands.Choice(name="Slot Bot",           value="slot_bot"),
    app_commands.Choice(name="Ez Panel Bot",       value="ezpanel_bot"),
]

def copy_files_from_directory(src_dir, dest_dir):
    """
    Copie uniquement les fichiers du dossier source (et de ses sous-dossiers)
    directement dans le dossier destination sans recréer la structure des dossiers.
    """
    for item in os.listdir(src_dir):
        s = os.path.join(src_dir, item)
        if os.path.isfile(s):
            shutil.copy2(s, dest_dir)
        elif os.path.isdir(s):
            copy_files_from_directory(s, dest_dir)

class KeyView(ui.View):
    def __init__(self, keys, app_name, amount, timeout=120):
        super().__init__(timeout=timeout)  # Timeout de 2 minutes
        self.keys = keys
        self.app_name = app_name
        self.amount = amount
        self.current_page = 0
        self.chunk_size = 50  # Nombre de clés par page
        self.total_pages = (len(keys) - 1) // self.chunk_size + 1

    def format_page(self):
        start = self.current_page * self.chunk_size
        end = start + self.chunk_size
        chunk = self.keys[start:end]
        keys_str = "\n".join(f"`{key}`" for key in chunk)
        displayed_amount = len(chunk)
        embed = discord.Embed(
            title=f"✅ Keys Generated",
            description=f"Activation keys generated for **{self.app_name}**:\n{keys_str}",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages} ・ {displayed_amount}/{self.amount} keys")
        return embed

    @ui.button(label="Previous", style=ButtonStyle.primary, disabled=True)
    async def previous_button(self, interaction: discord.Interaction, button: ui.Button):
        self.current_page -= 1
        if self.current_page == 0:
            button.disabled = True
        self.children[1].disabled = False  # Active le bouton "Next"
        await interaction.response.edit_message(embed=self.format_page(), view=self)

    @ui.button(label="Next", style=ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: ui.Button):
        self.current_page += 1
        if self.current_page == self.total_pages - 1:
            button.disabled = True
        self.children[0].disabled = False  # Active le bouton "Previous"
        await interaction.response.edit_message(embed=self.format_page(), view=self)

    @ui.button(label="Export .txt", style=ButtonStyle.success, emoji="📄")
    async def export_button_callback(self, interaction: discord.Interaction, button: ui.Button):
        file_name = f"{self.app_name}_keys.txt"
        with open(file_name, "w") as file:
            file.write("\n".join(self.keys))
        file_obj = File(file_name)
        await interaction.response.send_message(f"Exported **{self.amount}** keys for **{self.app_name}**", file=file_obj, ephemeral=True)

    @ui.button(label="Copy All", style=ButtonStyle.secondary, emoji="📋")
    async def copy_all_button_callback(self, interaction: discord.Interaction, button: ui.Button):
        keys_str = "\n".join(self.keys)
        await interaction.response.send_message(f"**Copied Keys:**\n{keys_str}", ephemeral=True)

    @ui.button(label="Phone Format", style=ButtonStyle.secondary, emoji="📱")
    async def phone_format_button_callback(self, interaction: discord.Interaction, button: ui.Button):
        keys_str = "\n".join(self.keys)
        await interaction.response.send_message(keys_str, ephemeral=True)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        expired_embed = discord.Embed(
            title="Expired",
            description="This message is no longer interactive.",
            color=discord.Color.red()
        )
        await self.message.edit(embed=expired_embed, view=None)

class SubscriptionManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = 'subscriptions.db'
        
        # Initialisation du client Docker
        self.docker_client = docker.from_env()
        
        # On démarre la task
        self.check_subscriptions.start()

    async def send_permission_error(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Error", description="You do not have permission to use this command.", color=0xFF0000)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def cog_load(self):
        # Initialize the database when the Cog is loaded
        await self.init_db()

    async def init_db(self):
        # Database initialization
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    activation_key TEXT,
                    assigned_bot TEXT,
                    bot_token TEXT,
                    container_name TEXT,
                    container_id TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    notified INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 0,
                    deletion_date TEXT
                )
            ''')

            # ✅ TABLE DES CLÉS D’ACTIVATION (Valid Keys)
            await db.execute('''
                CREATE TABLE IF NOT EXISTS valid_keys (
                    key TEXT PRIMARY KEY,
                    assigned_bot TEXT,
                    guild_id INTEGER,
                    is_used INTEGER DEFAULT 0,
                    used_at TEXT,
                    start_date TEXT,
                    end_date TEXT
                )
            ''')

            await db.commit()

    async def generate_custom_key(self, format_string: str) -> str:
        """
        Replaces '*' in format_string with random alphanumeric characters.
        Example: format_string="CAL-****-****" -> "CAL-AB12-3Z9X"
        """
        key = []
        for char in format_string:
            if char == '*':
                key.append(random.choice(string.ascii_uppercase + string.digits))
            else:
                key.append(char)
        return "".join(key)

    async def check_admin_permissions(self, interaction: discord.Interaction) -> bool:
        """
        Example permission check. Replace with your real admin logic.
        """
        # For instance, check if the user has 'administrator' permission in the guild:
        if interaction.user.guild_permissions.administrator:
            return True

        await interaction.response.send_message(
            "You don't have permission to use this command.",
            ephemeral=True
        )
        return False

    @tasks.loop(minutes=1)  # Check subscriptions every minute
    async def check_subscriptions(self):
        now = datetime.datetime.now()

        async with aiosqlite.connect(self.db_path) as db:
            # Select each row by id, because each row represents a single bot subscription
            async with db.execute('''
                SELECT id, user_id, assigned_bot, end_date, notified
                FROM subscriptions
            ''') as cursor:
                async for row in cursor:
                    row_id, user_id, assigned_bot, end_date_str, notified = row
                    end_date = datetime.datetime.fromisoformat(end_date_str)
                    user = self.bot.get_user(user_id)
                    time_remaining = end_date - now

                    # If we can't find this user in the guild or in cache, skip
                    if user is None:
                        continue

                    # For display in messages, we can just show assigned_bot 
                    # or map it to a friendly name if you prefer:
                    bot_display_str = assigned_bot

                    # 1) Try to fetch the role from your guild if it exists in ROLE_MAP
                    #    (If the user can be in multiple guilds, you might want a specific guild ID)
                    #    For example, if this manager bot is in exactly one guild you can do:
                    guild = self.bot.get_guild(GUILD_ID)  # Replace with your actual guild ID
                    role_id = ROLE_MAP.get(assigned_bot)
                    role = guild.get_role(role_id) if (guild and role_id) else None

                    # Check if we're less than 24 hours remaining
                    if datetime.timedelta(hours=0) < time_remaining <= datetime.timedelta(days=1):
                        if notified == 0:
                            # The user has not yet been notified
                            embed = discord.Embed(
                                title="⏰ Your subscription is ending soon!",
                                description=(
                                    f"Your subscription for **{bot_display_str}** "
                                    f"will expire in less than 24 hours."
                                ),
                                color=discord.Color.orange()
                            )
                            embed.add_field(
                                name="Data Retention Notice",
                                value=(
                                    "If you need to retain any data from your bots, "
                                    "please ensure to extract it before the subscription ends. "
                                    "If you need help, contact our support. We are not responsible "
                                    "for any data loss after expiration."
                                ),
                                inline=False
                            )
                            embed.add_field(
                                name="Renew Your Subscription",
                                value="Click the button below to renew your subscription and continue enjoying our services.",
                                inline=False
                            )
                            embed.set_footer(
                                text="Thank you for using our service!",
                                icon_url=footer_icon_link
                            )

                            # Buttons for renew and support
                            view = discord.ui.View()
                            view.add_item(discord.ui.Button(
                                label="Support",
                                style=discord.ButtonStyle.link,
                                url=support_url
                            ))
                            view.add_item(discord.ui.Button(
                                label="Renew Now",
                                style=discord.ButtonStyle.primary,
                                url=renewal_url
                            ))

                            await user.send(embed=embed, view=view)

                            # Notify admin channel
                            admin_channel = self.bot.get_channel(ADMIN_CHANNEL_ID)
                            if admin_channel:
                                await admin_channel.send(
                                    f"**[<:excla_icon_av_v2:1272927692743901224>]** "
                                    f"The subscription of **{user.name}** for **{bot_display_str}** "
                                    f"will expire in less than 24 hours."
                                )

                            # Mark user as notified in DB
                            await db.execute('''
                                UPDATE subscriptions
                                SET notified = 1
                                WHERE id = ?
                            ''', (row_id,))
                            await db.commit()

                    # Check if subscription is already expired
                    if now >= end_date:
                        if user:
                            embed = discord.Embed(
                                title="😢 Oh no, your subscription has expired!",
                                description=(
                                    f"Your subscription for **{bot_display_str}** has expired."
                                ),
                                color=discord.Color.red()
                            )
                            embed.add_field(
                                name="Renew Your Subscription",
                                value=(
                                    "Click the button below to renew your subscription "
                                    "and continue enjoying our services."
                                ),
                                inline=False
                            )
                            embed.set_footer(
                                text="Thank you for using our service!",
                                icon_url=footer_icon_link
                            )

                            view = discord.ui.View()
                            view.add_item(discord.ui.Button(
                                label="Renew Now",
                                style=discord.ButtonStyle.primary,
                                url=renewal_url
                            ))

                            await user.send(embed=embed, view=view)

                            admin_channel = self.bot.get_channel(ADMIN_CHANNEL_ID)
                            if admin_channel:
                                await admin_channel.send(
                                    f"**[<:moins_icon_av_v2:1272927693863915551>]** "
                                    f"The subscription of **{user.name}** for **{bot_display_str}** "
                                    f"has **expired**."
                                )
                                
                        # 2) If it's expired, remove the role (if role != None and user has it)
                        if role:
                            member = guild.get_member(user.id)
                            if member and role in member.roles:
                                await member.remove_roles(role, reason="Subscription expired")

                        # Remove only this specific row (one bot) from the DB
                        await db.execute('DELETE FROM subscriptions WHERE id = ?', (row_id,))
                        await db.commit()

                    else:
                        # 3) If it's still active (now < end_date), make sure the user has the role
                        if role:
                            member = guild.get_member(user.id)
                            if member and role not in member.roles:
                                await member.add_roles(role, reason="Subscription active")


    def calculate_new_end_date(self, current_end_date: datetime.datetime, duration: int, unit: str) -> datetime.datetime:
        multiplier = TIME_MULTIPLIERS.get(unit, TIME_MULTIPLIERS["Day"])  # Default to days
        return current_end_date + datetime.timedelta(seconds=duration * multiplier)

    @app_commands.command(name="add_sub", description="Add a subscription for a user")
    @app_commands.describe(
        duration="Duration of the subscription",
        unit="Time unit (Minute, Hour, Day, Week, Month)"
    )
    @app_commands.choices(
        unit=[
            app_commands.Choice(name="Minute", value="Minute"),
            app_commands.Choice(name="Hour", value="Hour"),
            app_commands.Choice(name="Day", value="Day"),
            app_commands.Choice(name="Week", value="Week"),
            app_commands.Choice(name="Month", value="Month"),
        ],
        bot1=AVAILABLE_BOTS, bot2=AVAILABLE_BOTS, bot3=AVAILABLE_BOTS,
        bot4=AVAILABLE_BOTS, bot5=AVAILABLE_BOTS, bot6=AVAILABLE_BOTS,
    )
    async def add_sub(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        duration: int,
        unit: str = "Day",
        bot1: str = None,
        bot2: str = None,
        bot3: str = None,
        bot4: str = None,
        bot5: str = None,
        bot6: str = None
    ):
        # Gather all chosen bots
        raw_selected = [bot1, bot2, bot3, bot4, bot5, bot6]
        # Filter out None
        bots_selected = [b for b in raw_selected if b]
        # (Optional) If you want to exclude "ML Sub." from the final embed,
        # you can do that here. Or leave as is if you want to allow it.

        # Calculate the end date based on chosen duration/unit
        end_date = self.calculate_new_end_date(datetime.datetime.now(), duration, unit)
        now_str = datetime.datetime.now().isoformat()

        # Insert one row PER bot in 'subscriptions'
        async with aiosqlite.connect(self.db_path) as db:
            for single_bot in bots_selected:
                await db.execute('''
                    INSERT INTO subscriptions (
                        user_id,
                        assigned_bot,
                        start_date,
                        end_date
                    )
                    VALUES (?, ?, ?, ?)
                ''', (
                    user.id,
                    single_bot,            # each row => one assigned_bot
                    now_str,
                    end_date.isoformat(),
                ))
            await db.commit()

        # Build a display string for success messages
        # (If you want to skip "ML Sub." from display, you can filter again)
        bots_display = bots_selected  # or [b for b in bots_selected if b != "ml_sub"]

        # Send the ephemeral success message
        await interaction.response.send_message(
            f"**[<:plus_icon_av_v2:1272927695117881465>]** Subscription added for {user.mention} "
            f"with bots: {', '.join(bots_display)} until {end_date.strftime(time_format)}"
        )

        # Also send an admin channel update if needed
        admin_channel = self.bot.get_channel(ADMIN_CHANNEL_ID)
        if admin_channel:
            await admin_channel.send(
                f"**[<:plus_icon_av_v2:1272927695117881465>]** Subscription added for {user.mention} "
                f"with bots: {', '.join(bots_display)} until {end_date.strftime(time_format)}"
            )

        # DM the user with an embed
        embed = discord.Embed(
            title="🎉 Your subscription has started!",
            description=f"Your bots **{', '.join(bots_display)}** are now live. We're excited to have you on board!",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Need Help?",
            value="Click the button below to contact our support team.",
            inline=False
        )
        embed.add_field(
            name="Get Started",
            value="Click the button below to view our official guide and get started with your new subscription.",
            inline=False
        )
        embed.set_image(url=embed_image_link)
        embed.set_footer(text="Thank you for choosing our service!", icon_url=footer_icon_link)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label="Support",
            style=discord.ButtonStyle.link,
            url=support_url  # Replace with your actual support URL
        ))
        view.add_item(discord.ui.Button(
            label="Official Guide",
            style=discord.ButtonStyle.link,
            url=guide_url
        ))

        try:
            await user.send(embed=embed, view=view)
        except discord.Forbidden:
            # If DMs are off, ignore or handle the error
            pass


    @app_commands.command(name="modify_sub", description="Modify a user's subscription duration and bots")
    @app_commands.describe(duration="Time to add/remove from the subscription", unit="Time unit (Minute, Hour, Day, Week, Month)")
    @app_commands.choices(unit=diff_durations, bot1=AVAILABLE_BOTS, bot2=AVAILABLE_BOTS, bot3=AVAILABLE_BOTS, bot4=AVAILABLE_BOTS, bot5=AVAILABLE_BOTS, bot6=AVAILABLE_BOTS)
    async def modify_sub(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        duration: int,
        unit: str = "Day",
        bot1: str = None,
        bot2: str = None,
        bot3: str = None,
        bot4: str = None,
        bot5: str = None,
        bot6: str = None
    ):
        # 1) We no longer keep a "bots" column, so remove or adapt references.
        #    Instead, each row is for one assigned_bot. If you want to modify
        #    multiple rows at once, you must loop or do an approach similar to add_sub.

        bots_selected = [b for b in [bot1, bot2, bot3, bot4, bot5, bot6] if b]

        # 2) Because we have one row per bot, we must decide how we pick
        #    WHICH row(s) to modify. For a minimal fix, if you want to update
        #    *all* rows of that user that match any of the selected bots, do:
        new_end_date = self.calculate_new_end_date(datetime.datetime.now(), duration, unit)

        async with aiosqlite.connect(self.db_path) as db:
            for single_bot in bots_selected:
                await db.execute('''
                    UPDATE subscriptions
                    SET end_date = ?
                    WHERE user_id = ?
                    AND assigned_bot = ?
                ''', (
                    new_end_date.isoformat(),
                    user.id,
                    single_bot
                ))
            await db.commit()

        # Finally, send success message
        await interaction.response.send_message(
            f"Subscription for {user.mention} modified. New end date: {new_end_date.strftime(time_format)}"
        )


    @app_commands.command(name="list_subs", description="List all active subscriptions")
    async def list_subs(self, interaction: discord.Interaction):
        # 1) We no longer store multiple bots in a single row. So let's select 'assigned_bot' for each row.
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT user_id, assigned_bot, end_date FROM subscriptions') as cursor:
                subscriptions = await cursor.fetchall()
                if not subscriptions:
                    await interaction.response.send_message("No active subscriptions.", ephemeral=True)
                    return

                description_lines = []
                for row in subscriptions:
                    user_id, assigned_bot, end_date_str = row
                    user = self.bot.get_user(user_id)
                    end_date = datetime.datetime.fromisoformat(end_date_str)
                    user_name = (
                        f"{user.mention} (`{user.name}` / `{user_id}`)"
                        if user else f"Unknown UserID {user_id}"
                    )

                    description_lines.append(
                        f"**{user_name}**\n- End on: {end_date.strftime(time_format)}\n"
                        f"- Bot: `{assigned_bot}`\n"
                    )

                embed = discord.Embed(
                    title="Active Subscriptions",
                    description="\n".join(description_lines),
                    color=discord.Color.green()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)


    @app_commands.command(name="check_sub", description="Check the status of your subscriptions")
    async def check_sub(self, interaction: discord.Interaction):
        user = interaction.user

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT assigned_bot, end_date
                FROM subscriptions
                WHERE user_id = ?
            ''', (user.id,))
            rows = await cursor.fetchall()

        if not rows:
            await interaction.response.send_message(
                f"No active subscription found for {user.mention}.",
                ephemeral=True
            )
            return

        now = datetime.datetime.now()
        line_list = []
        for assigned_bot, end_date_str in rows:
            end_date = datetime.datetime.fromisoformat(end_date_str)

            if now >= end_date:
                status = f"{off_emoji} Expired"
                color = discord.Color.red()
            else:
                status = f"{on_emoji} Active"
                color = discord.Color.green()

            line_list.append(
                f"**Bot:** `{assigned_bot}`\n"
                f"**Status:** {status}\n"
                f"**End Date:** {end_date.strftime(time_format)}"
            )

        description_str = "\n\n".join(line_list)
        embed = discord.Embed(
            title="Your Subscription(s)",
            description=description_str,
            color=discord.Color.green()
        )
        embed.set_footer(text="Thank you for choosing our service!", icon_url=footer_icon_link)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="activate", description="Activate your bot by providing an activation key.")
    @app_commands.describe(activation_key="The activation key provided by the admin or purchased.")
    async def activate(self, interaction: discord.Interaction, activation_key: str):
        """
        1) Checks the key in valid_keys and marks it used.
        2) Inserts/updates the subscription (in the subscriptions table) with a 30-day period.
        3) Informs the user to run /setup_bot to complete the setup.
        """
        user = interaction.user
        print(f"[DEBUG] {user} is trying to activate with key: {activation_key}")

        # Réponse immédiate pour éviter le timeout Discord
        await interaction.response.defer(ephemeral=True)

        try:
            # 1️⃣ Vérifier la clé dans la base de données
            print("[DEBUG] Connecting to database...")
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    'SELECT assigned_bot, is_used FROM valid_keys WHERE key = ?',
                    (activation_key,)
                ) as cursor:
                    row = await cursor.fetchone()

                if row is None:
                    print("[ERROR] Invalid key provided.")
                    embed = discord.Embed(
                        title="Invalid Key",
                        description="This activation key is invalid or does not exist.",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                assigned_bot, is_used = row
                if is_used == 1:
                    print("[ERROR] Key already used.")
                    embed = discord.Embed(
                        title="Key Already Used",
                        description="This activation key has already been used.",
                        color=discord.Color.yellow()
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                print(f"[DEBUG] Key validated for bot: {assigned_bot}")

                # 2️⃣ Marquer la clé comme utilisée
                now = datetime.datetime.now()
                await db.execute(
                    '''
                    UPDATE valid_keys
                    SET is_used = 1, used_at = ?
                    WHERE key = ?
                    ''',
                    (now.isoformat(), activation_key)
                )

                # 3️⃣ Ajouter la souscription dans la table subscriptions (30 jours par défaut)
                end_date = now + datetime.timedelta(days=30)
                await db.execute('''
                    INSERT OR REPLACE INTO subscriptions (user_id, activation_key, assigned_bot, start_date, end_date, is_active)
                    VALUES (?, ?, ?, ?, ?, 0)
                ''', (
                    user.id,
                    activation_key,
                    assigned_bot,  # <-- Valeur ajoutée ici !
                    now.isoformat(),
                    end_date.isoformat()
                ))
                await db.commit()
            
            print("[DEBUG] Subscription successfully registered.")

            # On ne copie plus les fichiers ici, c'est réservé à /setup_bot.
            embed = discord.Embed(
                title="Activation Complete!",
                description=(
                    f"Key `{activation_key}` has been activated for **{assigned_bot}**!\n"
                    "Next step: run `/setup_bot` to set up your bot server."
                ),
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            embed = discord.Embed(
                title="Unexpected Error",
                description=f"An error occurred: `{e}`",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    def copy_files_from_directory(src_dir, dest_dir):
        for item in os.listdir(src_dir):
            s = os.path.join(src_dir, item)
            # Copie directement les fichiers dans le dossier destination
            if os.path.isfile(s):
                shutil.copy2(s, dest_dir)
            elif os.path.isdir(s):
                # Copie récursive : pour chaque sous-dossier, copier son contenu dans dest_dir (sans recréer le sous-dossier)
                copy_files_from_directory(s, dest_dir)

    @app_commands.command(name="setup_bot", description="Register your Discord bot token and start your bot server.")
    @app_commands.describe(
        bot_token="The token of your Discord bot.",
        bot_choice="Which bot do you want to set up?"
    )
    @app_commands.choices(bot_choice=AVAILABLE_BOTS)
    async def setup_bot(
        self,
        interaction: discord.Interaction,
        bot_token: str,
        bot_choice: str
    ):
        """
        1) Checks subscriptions to ensure the subscription is active and not expired.
        2) Validates the provided bot token.
        3) Verifies that the user's folder exists.
        4) Verifies that the default bot source folder exists.
        5) Copies the default launcher and bot sources into the user's folder.
        6) Launches a Docker container with the user's code mounted.
        7) Updates the subscription record to mark the server as active.
        """
        user = interaction.user
        print(f"[DEBUG] User {user} triggered /setup_bot for {bot_choice} with token {bot_token}")

        await interaction.response.defer(ephemeral=True)

        # 1) Vérifier si une souscription active existe
        try:
            print("[DEBUG] Connecting to database for subscription check...")
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('''
                    SELECT end_date, is_active
                    FROM subscriptions
                    WHERE user_id = ?
                    AND assigned_bot = ?
                ''', (user.id, bot_choice)) as cursor:
                    row = await cursor.fetchone()
                    print(f"[DEBUG] Subscription query result: {row}")

                    if row is None:
                        print("[ERROR] No active subscription found")
                        embed = discord.Embed(
                            title="No Active Subscription",
                            description=(
                                f"You do not have an active subscription for `{bot_choice}`.\n"
                                "Please use `/activate` first to set up a subscription, or contact support."
                            ),
                            color=discord.Color.red()
                        )
                        await interaction.followup.send(embed=embed, ephemeral=True)
                        return

                    end_date_str, is_active = row
                    end_date = datetime.datetime.fromisoformat(end_date_str)
                    now = datetime.datetime.now()
                    print(f"[DEBUG] Subscription end date: {end_date}, now: {now}, is_active: {is_active}")

                    if now > end_date:
                        print("[ERROR] Subscription expired")
                        embed = discord.Embed(
                            title="Subscription Expired",
                            description=f"Your `{bot_choice}` subscription has expired. Please contact support to renew it.",
                            color=discord.Color.red()
                        )
                        await interaction.followup.send(embed=embed, ephemeral=True)
                        return

                    if is_active == 1:
                        print("[ERROR] Server already active")
                        embed = discord.Embed(
                            title="Server Already Active",
                            description=(
                                f"A server is already active for the `{bot_choice}` bot.\n"
                                "Please use `/stop_bot` before starting a new one."
                            ),
                            color=discord.Color.yellow()
                        )
                        await interaction.followup.send(embed=embed, ephemeral=True)
                        return
        except Exception as e:
            print(f"[ERROR] Database error: {e}")
            embed = discord.Embed(
                title="Database Error",
                description=f"An error occurred while checking subscription: {e}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # 2) Vérifier la validité du bot token (exemple : longueur minimale)
        if len(bot_token) < 50:
            print("[ERROR] Bot token appears invalid (too short)")
            embed = discord.Embed(
                title="Invalid Bot Token",
                description="The bot token provided appears to be invalid. Please check your token and try again.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        print("[DEBUG] Bot token passed simple validation.")

        # 3) Vérifier que le dossier utilisateur existe, sinon le créer
        user_folder = f"/absolute/path/to/clients_data/user_{user.id}"  # Adapté à votre configuration
        print(f"[DEBUG] Checking user folder at {user_folder}")
        if not os.path.exists(user_folder):
            print("[DEBUG] User folder not found, creating it...")
            try:
                os.makedirs(user_folder, exist_ok=True)
                print(f"[DEBUG] User folder created: {user_folder}")
            except Exception as e:
                print(f"[ERROR] Could not create user folder: {e}")
                embed = discord.Embed(
                    title="Folder Creation Error",
                    description=f"An error occurred while creating your folder: {e}",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

        # 4) Vérifier que le dossier source par défaut pour le bot existe
        default_bot_folder = BOT_SOURCE_MAP.get(bot_choice)
        print(f"[DEBUG] Checking default bot source folder for {bot_choice} at {default_bot_folder}")
        if not default_bot_folder or not os.path.exists(default_bot_folder):
            print(f"[ERROR] Default bot source folder for {bot_choice} not found!")
            embed = discord.Embed(
                title="Missing Default Bot Sources",
                description=(f"The default source folder for `{bot_choice}` was not found at `{default_bot_folder}`.\n"
                            "Please ensure that the bot sources have been set up correctly on the server."),
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # 5) Copier uniquement les fichiers contenus dans les dossiers source dans le dossier utilisateur
        # Copier les fichiers du dossier "launcher" (contenant bot.py et la configuration globale)
        launcher_folder = "def_bot_srcs/launcher"
        print(f"[DEBUG] Checking launcher folder at {launcher_folder}")
        if not os.path.exists(launcher_folder):
            print("[ERROR] Launcher folder not found!")
            embed = discord.Embed(
                title="Missing Launcher Folder",
                description="The default launcher folder was not found. Please ensure it exists.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        try:
            print("[DEBUG] Cleaning user folder...")
            if os.path.exists(user_folder):
                shutil.rmtree(user_folder)
            os.makedirs(user_folder, exist_ok=True)
            print(f"[DEBUG] User folder created: {user_folder}")

            print("[DEBUG] Copying files from launcher folder...")
            copy_files_from_directory(launcher_folder, user_folder)
            print("[DEBUG] Launcher files copied successfully.")

            # Copier les fichiers du dossier du bot choisi (seulement les fichiers, pas le dossier entier)
            default_bot_folder = BOT_SOURCE_MAP.get(bot_choice)
            print(f"[DEBUG] Checking default bot source folder for {bot_choice} at {default_bot_folder}")
            if not default_bot_folder or not os.path.exists(default_bot_folder):
                print(f"[ERROR] Default bot source folder for {bot_choice} not found!")
                embed = discord.Embed(
                    title="Missing Default Bot Sources",
                    description=(f"The default source folder for `{bot_choice}` was not found at `{default_bot_folder}`.\n"
                                "Please ensure that the bot sources have been set up correctly on the server."),
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            print(f"[DEBUG] Copying files from {default_bot_folder} to {user_folder}...")
            copy_files_from_directory(default_bot_folder, user_folder)
            print("[DEBUG] Bot source files copied successfully.")

            # Copier explicitement requirements.txt si présent dans le dossier source du bot
            req_source = os.path.join(default_bot_folder, "requirements.txt")
            req_dest = os.path.join(user_folder, "requirements.txt")
            if os.path.isfile(req_source):
                try:
                    shutil.copy2(req_source, req_dest)
                    print("[DEBUG] requirements.txt copied successfully from default bot folder to user folder.")
                except Exception as e:
                    print(f"[ERROR] Failed to copy requirements.txt: {e}")
            else:
                print("[WARNING] requirements.txt not found in the default bot folder.")
        except Exception as e:
            print(f"[ERROR] Error copying source files: {e}")
            embed = discord.Embed(
                title="File Copy Error",
                description=f"An error occurred while copying source files: {e}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # 6) Lancer le conteneur Docker
        container_name = f"discordbot_{user.id}" # def = discordbot_{user.id}_{bot_choice}
        print(f"[DEBUG] Attempting to launch Docker container: {container_name}")
        try:
            container = self.docker_client.containers.run(
                image="ghcr.io/parkervcp/yolks:bot_red",
                name=container_name,
                detach=True,
                working_dir="/home/container",  # Ajouté ici
                environment={
                    "DISCORD_TOKEN": bot_token,
                    "STARTUP": "pip install -r requirements.txt && python bot.py"
                },
                mem_limit="128m",
                volumes={
                    os.path.abspath(user_folder): {
                        "bind": "/home/container",
                        "mode": "rw"
                    }
                }
            )
            print(f"[DEBUG] Docker container started successfully: {container.id}")
        except docker.errors.APIError as e:
            print(f"[ERROR] Docker error: {e}")
            embed = discord.Embed(
                title="Server Launch Error",
                description=f"Error while launching your bot server: {e.explanation}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return


        # 7) Mettre à jour la base de données pour marquer le bot comme actif
        print("[DEBUG] Updating database to mark server as active")
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE subscriptions
                    SET bot_token = ?, container_id = ?, container_name = ?, is_active = 1
                    WHERE user_id = ?
                    AND assigned_bot = ?
                ''', (
                    bot_token,
                    container.id,
                    container_name,
                    user.id,
                    bot_choice
                ))
                await db.commit()
                print("[DEBUG] Database updated successfully")
        except Exception as e:
            print(f"[ERROR] Failed to update database: {e}")
            embed = discord.Embed(
                title="Database Update Error",
                description=f"Failed to update subscription status: {e}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # 7.1) Mettre à jour le fichier config.json avec les données du bot dans le dossier utilisateur (docker)
        try:
            config_path = os.path.join(user_folder, "config.json")  # Le fichier config.json sera dans le dossier utilisateur
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            else:
                config_data = {}

            # On attend que le fichier ait la structure : { "bots": { ... } }
            if "bots" not in config_data:
                config_data["bots"] = {}

            # Mettre à jour la configuration pour le bot sélectionné
            config_data["bots"][bot_choice] = {
                "token": bot_token,
                "command_prefix": "!",           # Vous pouvez modifier cette valeur si nécessaire
                "extensions": [bot_choice],  # Par défaut, ou laissez [] si vous ne voulez pas le gérer ici # ["cogs." + bot_choice] (old)
                "custom_status": ["Online", "watching"]
            }

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)
            print("[DEBUG] config.json updated successfully in the user folder")
        except Exception as e:
            print(f"[ERROR] Failed to update config.json: {e}")



        # 8) Envoyer le message de succès
        print("[DEBUG] Sending success message to user")
        embed = discord.Embed(
            title="Server Online",
            description=(
                f"Your `{bot_choice}` bot server is now online!\n"
                f"**Server ID:** `{container.id}`"
            ),
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        print("[DEBUG] /setup_bot completed successfully")

    @app_commands.command(name="restart_bot", description="Restart or start your bot server.")
    @app_commands.describe(bot_choice="The bot you want to restart. Leave blank if you only have one bot.")
    @app_commands.choices(bot_choice=AVAILABLE_BOTS)
    async def restart_bot(
        self,
        interaction: discord.Interaction,
        bot_choice: Optional[str] = None
    ):
        """
        If the bot is active, restart it; if it is inactive, start it.
        """
        user = interaction.user
        print(f"[DEBUG] User {user} triggered /restart_bot with bot_choice: {bot_choice}")

        await interaction.response.defer(ephemeral=True)

        # 1) Récupérer la souscription active pour ce bot dans la table subscriptions
        async with aiosqlite.connect(self.db_path) as db:
            # On récupère toutes les souscriptions actives pour l'utilisateur
            cursor = await db.execute('''
                SELECT assigned_bot, container_id, is_active
                FROM subscriptions
                WHERE user_id = ? AND is_active = 1
            ''', (user.id,))
            rows = await cursor.fetchall()

        if not rows:
            embed = discord.Embed(
                title="No Active Bot Found",
                description="You do not have any active bot subscriptions for the specified bot.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # 2) Si plusieurs souscriptions et bot_choice non précisé, demander à préciser
        if len(rows) > 1 and not bot_choice:
            embed = discord.Embed(
                title="Multiple Active Bots Found",
                description="You have multiple active bot subscriptions. Please specify which one to restart (e.g. `/restart_bot bot_choice:<YourBot>`).",
                color=discord.Color.yellow()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # 3) Déterminer la souscription à utiliser
        if len(rows) == 1 and not bot_choice:
            assigned_bot, container_id, is_active = rows[0]
        else:
            matched = [r for r in rows if r[0] == bot_choice]
            if not matched:
                embed = discord.Embed(
                    title="Invalid Bot Choice",
                    description=f"You do not have an active subscription for bot: `{bot_choice}`.\nPlease pick a valid bot.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            assigned_bot, container_id, is_active = matched[0]

        # 4) Récupérer le conteneur Docker
        try:
            container = self.docker_client.containers.get(container_id)
        except Exception as e:
            embed = discord.Embed(
                title="Container Retrieval Error",
                description=f"Could not retrieve the container with ID {container_id}: {e}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # 5) Selon l'état, redémarrer ou démarrer le conteneur
        try:
            if is_active == 1:
                print(f"[DEBUG] Restarting active container {container.id}")
                container.restart()  # Restart un conteneur actif
                action = "restarted"
            else:
                print(f"[DEBUG] Starting inactive container {container.id}")
                container.start()    # Démarrer un conteneur arrêté
                action = "started"
        except Exception as e:
            embed = discord.Embed(
                title="Restart/Start Error",
                description=f"An error occurred while restarting/starting your bot server: {e}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # 6) Mettre à jour la souscription pour marquer le bot comme actif
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE subscriptions
                SET is_active = 1
                WHERE user_id = ? AND assigned_bot = ?
            ''', (user.id, assigned_bot))
            await db.commit()
            print("[DEBUG] Subscription record updated to active.")

        embed = discord.Embed(
            title="Bot Restarted",
            description=f"Your `{assigned_bot}` bot server has been successfully {action}.",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        print("[DEBUG] /restart_bot completed successfully")


    @app_commands.command(name="stop_bot", description="Manually stop one of your active bot servers.")
    @app_commands.describe(bot_choice="The bot you want to stop. Leave blank if you only have one bot.")
    @app_commands.choices(bot_choice=AVAILABLE_BOTS)
    async def stop_bot(
        self,
        interaction: discord.Interaction,
        bot_choice: Optional[str] = None
    ):
        """
        Command to manually stop the user's active bot server.
        If the user has only one bot, they can omit the parameter.
        Otherwise, they must choose which bot to stop.
        """
        user = interaction.user

        async with aiosqlite.connect(self.db_path) as db:
            # Fetch all active bot subscriptions for this user from subscriptions table
            cursor = await db.execute('''
                SELECT assigned_bot, container_id, is_active
                FROM subscriptions
                WHERE user_id = ? AND is_active = 1
            ''', (user.id,))
            rows = await cursor.fetchall()

        if not rows:
            embed = discord.Embed(
                title="No Bot Found",
                description="You don't have any registered bot subscriptions.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # If user has more than one row and didn't specify a bot_choice => ask them to pick
        if len(rows) > 1 and not bot_choice:
            embed = discord.Embed(
                title="Multiple Bots Found",
                description=(
                    "You have multiple bot servers. Please specify which one to stop.\n"
                    "Example: `/stop_bot bot_choice:<YourBot>`"
                ),
                color=discord.Color.yellow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # If user has exactly one row and didn't specify a bot, use that row
        if len(rows) == 1 and not bot_choice:
            assigned_bot, container_id, is_active = rows[0]
        else:
            # There's either multiple rows and we have a bot_choice,
            # or there's a single row but the user explicitly typed a bot_choice anyway.

            # Attempt to match the row by assigned_bot == bot_choice
            matched = [r for r in rows if r[0] == bot_choice]
            if not matched:
                embed = discord.Embed(
                    title="Invalid Choice",
                    description=(
                        f"You do not have an active subscription for bot: `{bot_choice}`.\n"
                        "Please pick a valid bot that you own."
                    ),
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            assigned_bot, container_id, is_active = matched[0]

        # Now we have assigned_bot, container_id, is_active
        if is_active == 0:
            embed = discord.Embed(
                title="Already Inactive",
                description=(
                    f"Your `{assigned_bot}` bot is already inactive."
                ),
                color=discord.Color.yellow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Stop the container
        try:
            container = self.docker_client.containers.get(container_id)
            container.stop()
        except Exception as e:
            embed = discord.Embed(
                title="Stop Error",
                description=f"Error while stopping your `{assigned_bot}` bot server: {e}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Mark it inactive in subscriptions
        """async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE subscriptions
                SET is_active = 0
                WHERE user_id = ?
                AND assigned_bot = ?
            ''', (user.id, assigned_bot))
            await db.commit()"""

        embed = discord.Embed(
            title="Bot Stopped",
            description=(
                f"Your `{assigned_bot}` bot has been successfully stopped."
            ),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


    @app_commands.command(name="my_bots", description="Displays all your current bot servers (including both active and inactive).")
    async def my_bots(self, interaction: discord.Interaction):
        """
        Shows every bot server belonging to the user in 'user_bots' table,
        including server name, status (active/inactive), and end date.
        """
        user = interaction.user

        # We'll build a map from internal bot value -> user-facing name
        reverse_map = {choice.value: choice.name for choice in AVAILABLE_BOTS}

        # Fetch all rows for this user from user_bots
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT assigned_bot, container_id, is_active, end_date
                FROM user_bots
                WHERE user_id = ?
            ''', (user.id,))
            rows = await cursor.fetchall()

        # If none found, let the user know
        if not rows:
            embed = discord.Embed(
                title="No Bot Servers Found",
                description="You currently don't have any bot servers.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Otherwise, build a nice embed listing them
        lines = []
        now = datetime.datetime.now()
        for assigned_bot, container_id, is_active, end_date_str in rows:
            # Convert internal "paypal_bot" to user-friendly "PayPal Bot"
            bot_display_name = reverse_map.get(assigned_bot, assigned_bot)
            
            # Active or Inactive
            status_str = "Active" if is_active == 1 else "Inactive"
            
            # If you stored end_date in ISO format
            end_date = datetime.datetime.fromisoformat(end_date_str)
            remaining_days = (end_date - now).days
            
            # Build one line per bot server
            lines.append(
                f"**Bot:** {bot_display_name}\n"
                f"**Server ID:** `{container_id if container_id else 'N/A'}`\n"
                f"**Status:** {status_str}\n"
                f"**Subscription Ends:** {end_date_str} (in {remaining_days} days)\n"
            )

        description = "\n".join(lines)
        embed = discord.Embed(
            title="Your Bot Servers",
            description=description,
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="create_key", description="Create one or multiple activation keys for a specific bot.")
    @app_commands.describe(
        quantity="How many keys to generate at once.",
        format="Optional custom format with '*' wildcards. (e.g. BOT-****-****)",
        bot_choice="Which bot this key is for.",
        duration="Duration of the subscription",
        unit="Time unit (Minute, Hour, Day, Week, Month)"
    )
    @app_commands.choices(
        bot_choice=AVAILABLE_BOTS,
        unit=diff_durations
    )
    async def create_key(
        self,
        interaction: discord.Interaction,
        quantity: int,
        bot_choice: str,
        duration: int,
        unit: str,
        format: Optional[str] = None
    ):
        """
        Generates 'quantity' new keys, optionally matching a custom 'format',
        assigns them to the chosen bot, and stores them in valid_keys table.
        """

        if not await self.check_admin_permissions(interaction):
            return

        if quantity <= 0:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Error",
                    description="Quantity must be a positive integer.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return

        if format and not re.match(r'^[A-Za-z0-9\-\*]+$', format):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Invalid Format",
                    description="Use only letters, numbers, dashes, and '*' wildcards.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        keys = []
        try:
            if format:
                unique_attempts = 0
                max_attempts = quantity * 3
                while len(keys) < quantity and unique_attempts < max_attempts:
                    new_key = await self.generate_custom_key(format)
                    if new_key not in keys:
                        keys.append(new_key)
                    unique_attempts += 1

                if len(keys) < quantity:
                    await interaction.followup.send(
                        embed=discord.Embed(
                            title="Not Enough Unique Keys",
                            description="❌ Could not generate enough unique keys with the given format.",
                            color=discord.Color.red()
                        ),
                        ephemeral=True
                    )
                    return
            else:
                keys = [str(uuid.uuid4()) for _ in range(quantity)]

            duration_seconds = TIME_MULTIPLIERS.get(unit, TIME_MULTIPLIERS["Day"]) * duration
            guild_id = interaction.guild_id
            now = datetime.datetime.now()
            end_date = now + datetime.timedelta(seconds=duration_seconds)

            async with aiosqlite.connect(self.db_path) as db:
                await db.executemany('''
                    INSERT INTO valid_keys (key, assigned_bot, guild_id, is_used, used_at, start_date, end_date)
                    VALUES (?, ?, ?, 0, NULL, ?, ?)
                ''', [
                    (k, bot_choice, guild_id, now.isoformat(), end_date.isoformat()) for k in keys
                ])
                await db.commit()

            if len(keys) > 50:
                view = KeyView(keys, app_name=bot_choice, amount=quantity)
                message = await interaction.followup.send(embed=view.format_page(), view=view, ephemeral=True)
                view.message = message
            else:
                keys_str = "\n".join(f"`{key}`" for key in keys)
                embed = discord.Embed(
                    title="Keys Generated Successfully",
                    description=f"**Bot Assigned:** `{bot_choice}`\n**Duration:** `{duration} {unit}`\n\n**Generated Keys:**\n{keys_str}",
                    color=discord.Color.green()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            await interaction.followup.send(embed=discord.Embed(title="Error", description=f"❌ {e}", color=discord.Color.red()), ephemeral=True)



    @app_commands.command(name="check_all_keys", description="Displays total, used, and unused keys for each bot.")
    async def check_all_keys(self, interaction: discord.Interaction):
        """Shows a summary of key usage across all bots."""
        # 1) Admin permission check
        if not await self.check_admin_permissions(interaction):
            return

        # 2) Build a map from internal bot value -> user-facing name
        bot_name_map = {choice.value: choice.name for choice in AVAILABLE_BOTS}

        # 3) Query the database to group keys by assigned_bot
        async with aiosqlite.connect(self.db_path) as db:
            # For each assigned_bot, get total keys and how many are used
            # If "is_used" is stored as 0/1, summing it = number of used keys
            rows = await db.execute(
                '''
                SELECT assigned_bot,
                    COUNT(*) as total,
                    SUM(is_used) as used_count
                FROM valid_keys
                GROUP BY assigned_bot
                '''
            )
            results = await rows.fetchall()

        # If there are no keys at all
        if not results:
            embed = discord.Embed(
                title="No Keys Found",
                description="There are no keys in the database.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # 4) Build the embed lines
        lines = []
        for assigned_bot, total, used_count in results:
            used_count = used_count if used_count else 0  # handle None
            unused_count = total - used_count

            # If we want to display a user-facing name, check in bot_name_map
            friendly_name = bot_name_map.get(assigned_bot, assigned_bot)

            lines.append(
                f"**{friendly_name}**\n"
                f"Total Keys: `{total}`\n"
                f"Used Keys: `{used_count}`\n"
                f"Unused Keys: `{unused_count}`\n"
            )

        description = "\n".join(lines)

        # 5) Send the embed
        embed = discord.Embed(
            title="All Keys Overview",
            description=description,
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(SubscriptionManager(bot))
    await bot.tree.sync()