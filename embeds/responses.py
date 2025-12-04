import discord


class SuccessEmbed(discord.Embed):
    def __init__(self, message: str):
        super().__init__(
            title="✅ Success",
            description=message,
            color=discord.Colour.green(),
        )


class ErrorEmbed(discord.Embed):
    def __init__(self, message: str):
        super().__init__(
            title="❌ Error",
            description=message,
            color=discord.Colour.red(),
        )


class InfoEmbed(discord.Embed):
    def __init__(self, message: str):
        super().__init__(
            title="ℹ️ Info",
            description=message,
            color=discord.Colour.blue(),
        )


class WarningEmbed(discord.Embed):
    def __init__(self, message: str):
        super().__init__(
            title="⚠️ Warning",
            description=message,
            color=discord.Colour.gold(),
        )
