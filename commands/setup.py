import discord
from discord import Bot, ApplicationContext, CategoryChannel
from discord.ext.commands import Cog

from embeds.responses import SuccessEmbed, ErrorEmbed
import structlog

log = structlog.get_logger()


class Setup(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @discord.slash_command(name="setup", description="Setup tickets in your server")
    @discord.guild_only()
    @discord.default_permissions(administrator=True)
    async def setup(
        self,
        ctx: ApplicationContext,
        category_name: discord.Option(
            str,
            description="The custom name of the category for tickets",
            default="Tickets",
        ),
        ticket_admin_role: discord.Option(
            discord.Role,
            description="The role that should have access to the category",
            required=True,
        ),
    ):
        try:
            category: CategoryChannel = await ctx.guild.create_category(category_name)

            # Deny @everyone from viewing the category
            everyone_role = ctx.guild.default_role
            await category.set_permissions(
                everyone_role,
                view_channel=False,
            )

            # Allow the specified role to view the category
            if ticket_admin_role:
                await category.set_permissions(
                    ticket_admin_role,
                    view_channel=True,
                )

            await ctx.respond(
                embed=SuccessEmbed(f"Successfully created category `{category_name}`!"),
                ephemeral=True,
            )

        except discord.Forbidden:
            await ctx.respond(
                embed=ErrorEmbed(
                    "I don't have permission to create categories or manage permissions. Please check my permissions."
                ),
                ephemeral=True,
            )

        except Exception as e:
            await ctx.respond(
                embed=ErrorEmbed("Failed to create category, try again later."),
                ephemeral=True,
            )

            log.error(
                "Failed to create category in setup",
                error=str(e),
                channel_id=ctx.channel_id,
                user_id=ctx.user.id,
                guild_id=ctx.guild_id if ctx.guild else None,
            )


def setup(bot: Bot):
    bot.add_cog(Setup(bot))
