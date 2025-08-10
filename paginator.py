from typing import Callable, Any

import discord.ui
from discord import Interaction, Embed, Message
from discord import Button


class Paginator(discord.ui.View):

    def __init__(self, embed_caller: Callable, max_page: int, args: Any = None):
        self.embed_caller = embed_caller
        self.current_page = 0
        self.max_page = max_page
        self.message: Message | None = None
        self.args = args
        super().__init__(timeout=30)

    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.blurple)
    async def previous(self, interaction: Interaction, button: Button):
        self.current_page = max(0, self.current_page-1)
        self.update_buttons()
        new_embed = self.embed_caller(page=self.current_page, args=self.args)
        new_embed.set_footer(text=f"Page {self.current_page + 1} of {self.max_page}")
        await interaction.response.edit_message(embed=new_embed, view=self)

    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.blurple)
    async def next(self, interaction: Interaction, button: Button):
        self.current_page = min(self.max_page-1, self.current_page+1)
        self.update_buttons()
        new_embed: Embed = self.embed_caller(page=self.current_page, args=self.args)
        new_embed.set_footer(text=f"Page {self.current_page+1} of {self.max_page}")
        await interaction.response.edit_message(embed=new_embed, view=self)

    def update_buttons(self):
        # Disable back if on first page
        self.children[0].disabled = self.current_page == 0
        # Disable forward if on last page
        self.children[1].disabled = self.current_page == self.max_page-1

    def call(self) -> Embed:
        self.update_buttons()
        return self.embed_caller(page=self.current_page, args=self.args)

    async def on_timeout(self):
        await self.message.edit(content="Command timed out.", embed=None, view=None)

    @staticmethod
    def total_pages(results: int, results_per_page: int) -> int:
        extra = 1 if results % results_per_page > 0 else 0
        return (results // results_per_page) + extra
