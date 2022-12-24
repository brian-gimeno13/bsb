import discord

buttons = {}


class Difficulty(discord.ui.View):

    def __init__(self, best_match, author):
        self.author = author
        self.best_match = best_match
        super().__init__(timeout=None)
        for button in self.children:
            buttons[button.label] = button

    @discord.ui.button(label='Easy', style=discord.ButtonStyle.green)
    async def get_easy(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        buttons.get('Normal').disabled = False
        await interaction.response.edit_message(content=self.best_match['Easy'], view=self)

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='Normal', style=discord.ButtonStyle.red, disabled=True)
    async def get_normal(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        buttons.get('Easy').disabled = False
        await interaction.response.edit_message(content=self.best_match['Normal'], view=self)

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.author.id