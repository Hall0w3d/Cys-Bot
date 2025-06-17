import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import get
from discord import ui
import random
import os
import sqlite3
import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticket-setup", description="use this command to set up the tickets (cys only)")
    async def ticketsetup(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command :x:", ephemeral=True)
            return
        con = sqlite3.connect('stats.db')
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS stats
              (id TEXT PRIMARY KEY, claimed INT, closed INT)''')
        con.commit()
        con.close()

        guild = interaction.guild
        role = discord.utils.get(interaction.guild.roles, name="Ticket Support")
        channel_name = f"ticket-{interaction.user.name}"
        category = discord.utils.get(guild.categories, id=1345501998727823530)

        class cyssywizzy(ui.Modal):
            def __init__(self):
                super().__init__(title="Create Ticket")

                self.answer1 = ui.TextInput(label="What game is this issue on?", style=discord.TextStyle.short, placeholder="Example: ALS", required=True, max_length=20)
                self.answer2 = ui.TextInput(label="What is the issue?", style=discord.TextStyle.short, placeholder="Example: Doesnt detect unit placement", required=True, max_length=100)

                self.add_item(self.answer1)
                self.add_item(self.answer2)

            async def on_submit(self, interaction: discord.Interaction):

                class claimclose(discord.ui.View):
                    def __init__(self, timeout=None):
                        super().__init__(timeout=timeout)

                    @discord.ui.button(style=discord.ButtonStyle.red, label="Close", emoji="🔒")
                    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
                        cocks = False
                        for rolee in interaction.user.roles:
                            if rolee == role:
                                cocks = True
                                break
                        if not cocks:
                            await interaction.response.send_message(":x: You do not have permission to close this ticket!", ephemeral=True)
                            return
                        
                        con = sqlite3.connect("stats.db")
                        cur = con.cursor()

                        cur.execute("SELECT * FROM stats WHERE id = ?", (interaction.user.id,))
                        result = cur.fetchone()
                        if result is None:
                            if result is None:
                                cur.execute("INSERT INTO stats (id, claimed, closed) VALUES (?, ?, ?)", (interaction.user.id, 0, 1))
                        else:
                            cur.execute("UPDATE stats SET claimed = claimed, closed = closed + 1 WHERE id = ?", (interaction.user.id,))
                        con.commit()
                        con.close()

                        await interaction.response.send_message("Closing Ticket...")
                        await channel.delete()

                    @discord.ui.button(style=discord.ButtonStyle.green, label="Claim", emoji="👤")
                    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
                        cocks = False
                        for rolee in interaction.user.roles:
                            if rolee == role:
                                cocks = True
                                break
                        if not cocks:
                            await interaction.response.send_message(":x: You do not have permission to claim this ticket!", ephemeral=True)
                            return
                        

                        embed = discord.Embed(title="Claimed", color=discord.Color.green())
                        embed.add_field(name="", value=f"<@{interaction.user.id}> has claimed the ticket.")

                        con = sqlite3.connect("stats.db")
                        cur = con.cursor()

                        cur.execute("SELECT * FROM stats WHERE id = ?", (interaction.user.id,))
                        result = cur.fetchone()
                        if result is None:
                            if result is None:
                                cur.execute("INSERT INTO stats (id, claimed, closed) VALUES (?, ?, ?)", (interaction.user.id, 1, 0))
                        else:
                            cur.execute("UPDATE stats SET claimed = claimed + 1, closed = closed WHERE id = ?", (interaction.user.id,))
                        con.commit()
                        con.close()

                        self.remove_item(button)
                        await interaction.response.edit_message(view=self)
                        await interaction.followup.send(embed=embed)


                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                    role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
                }
                channel = await interaction.guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)

                embed = discord.Embed(title=f"", color=discord.Color.blue())
                embed.add_field(name=f"Ticket Created", value=f"Thanks {interaction.user.name} for contacting the support team of **Cys**!\nPlease explain your case so we can help you as quickly as possible, and **make sure to post a clip/screen shot of the issue**!")

                embed2 = discord.Embed(title=f"Answers", color=discord.Color.blue())
                embed2.add_field(name=f"Q1: What game is this issue on?", value=f"*{self.answer1.value}*", inline=False)
                embed2.add_field(name=f"Q2: What is the issue?", value=f"*{self.answer2.value}*", inline=False)

                view=claimclose(timeout=None)
                if channel:
                    await channel.send(f"<@{interaction.user.id}> , <@&{role.id}>", embeds=[embed, embed2], view=view)
                await interaction.response.send_message(f"Ticket <#{channel.id}> has been created :white_check_mark:", ephemeral=True)

        class create_ticket(discord.ui.View):
            def __init__(self, timeout=None):
                super().__init__(timeout=timeout)

            @discord.ui.button(style=discord.ButtonStyle.gray, label="Create Ticket", emoji="🛠️")
            async def create_ticket2(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.send_modal(cyssywizzy())

        embed = discord.Embed(title=f"Create a Ticket", color=discord.Color.blue())
        embed.add_field(name=f"", value=f"Click on the button below to create a support ticket.")

        await interaction.response.send_message(embed=embed, view=create_ticket())

    @app_commands.command(name="individual-stat", description="Checks the stats for one person")
    async def db(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command :x:", ephemeral=True)
            return
        con = sqlite3.connect("stats.db")
        cur = con.cursor()

        cur.execute("SELECT claimed FROM stats WHERE id = ?", (interaction.user.id,))
        claimed = cur.fetchone()[0]

        cur.execute("SELECT closed FROM stats WHERE id = ?", (interaction.user.id,))
        closed = cur.fetchone()[0]

        embed = discord.Embed(title=f"{interaction.user.name}'s Stats", color=discord.Color.blue())
        embed.add_field(name=f"", value=f"**Claims**: {claimed}")
        embed.add_field(name=f"", value=f"**Closes**: {closed}")
        embed.set_image(url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stats", description="Show overall support staff claims and closes (top 10)")
    async def stats(self, interaction: discord.Interaction, role: discord.Role = None):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command :x:", ephemeral=True)
            return
        con = sqlite3.connect("stats.db")
        cur = con.cursor()
        cur.execute("SELECT id, claimed, closed FROM stats")
        rows = cur.fetchall()
        con.close()

        ranks = sorted(rows, key=lambda row: row[1] + row[2], reverse=True)

        text = ""
        pages = []
        page_size = 10

        if role:
            filtered = []
            for user_id, claimed, closed in rows:
                member = interaction.guild.get_member(int(user_id))
                if member and role in member.roles:
                    filtered.append((member, claimed, closed))
            data = sorted(filtered, key=lambda row: row[1] + row[2], reverse=True)
            title = f"📊 Top ({role.name})"
        else:
            data = sorted(rows, key=lambda row: row[1] + row[2], reverse=True)
            title = "📊 Top Support Staff"

        

        if role:
            chunks = [data[i:i + page_size] for i in range(0, len(data), page_size)]
            for chunk in chunks:
                desc = ""
                for r, (member, claimed, closed) in enumerate(chunk, start=1):
                    total = claimed + closed
                    desc += f"**{r}.** {member.mention} — Claims: {claimed}, Closes: {closed} (Total: {total})\n"
                embed = discord.Embed(title=title, description=desc or "No data", color=discord.Color.purple())
                pages.append(embed)
        else:
            chunks = [data[i:i + page_size] for i in range(0, len(data), page_size)]
            for chunk in chunks:
                desc = ""
                for r, (user_id, claimed, closed) in enumerate(chunk, start=1):
                    user = await interaction.client.fetch_user(int(user_id))
                    total = claimed + closed
                    desc += f"**{r}.** {user.mention} — Claims: {claimed}, Closes: {closed} (Total: {total})\n"
                embed = discord.Embed(title=title, description=desc or "No data", color=discord.Color.purple())
                pages.append(embed)

        if not pages:
            await interaction.response.send_message("❌ No matching data found.", ephemeral=True)
            return    

        class Paginator(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.page = 0
                self.msg = None

            @discord.ui.button(label="◀️ Prev", style=discord.ButtonStyle.gray)
            async def prev(self, interaction2: discord.Interaction, button: discord.Button):
                if self.page > 0:
                    self.page -= 1
                    await interaction2.response.edit_message(embed=pages[self.page], view=self)

            @discord.ui.button(label="▶️ Next", style=discord.ButtonStyle.gray)
            async def next(self, interaction2: discord.Interaction, button: discord.Button):
                if self.page < len(pages) - 1:
                    self.page += 1
                    await interaction2.response.edit_message(embed=pages[self.page], view=self)

        view = Paginator()
        await interaction.response.send_message(embed=pages[0], view=view)

    @app_commands.command(name="clear-stats", description="clears all of the stats")
    async def clear(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command :x:", ephemeral=True)
            return
        con = sqlite3.connect('stats.db')
        cur = con.cursor()
        cur.execute('''DROP TABLE stats''')
        con.commit()
        con.close()

        con = sqlite3.connect('stats.db')
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS stats
            (id TEXT PRIMARY KEY, claimed INT, closed INT)''')
        con.commit()
        con.close()

        await interaction.response.send_message("Cleared DB ⚙️", ephemeral=True)

    async def cog_load(self):
        guild = discord.Object(id=1338965034616881263)
        self.bot.tree.add_command(self.stats, guild=guild)
        self.bot.tree.add_command(self.db, guild=guild)
        self.bot.tree.add_command(self.ticketsetup, guild=guild)
        self.bot.tree.add_command(self.clear, guild=guild)


async def setup(bot):
    await bot.add_cog(Tickets(bot))