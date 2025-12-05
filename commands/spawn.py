import discord
from discord import Bot, ApplicationContext
from discord.ext.commands import Cog
from views.open_ticket import OpenTicketView
from embeds.open_ticket import OpenTicketEmbed
from embeds.responses import ErrorEmbed, SuccessEmbed
import structlog

log = structlog.get_logger()


class SpawnButton(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @discord.slash_command(
        name="publish",
        description="Send a panel for users to create tickets in this channel",
    )
    @discord.guild_only()
    @discord.default_permissions(administrator=True)
    async def publish(self, ctx: ApplicationContext):
        try:
            channel = ctx.channel

            # Check if bot has permission to send messages in the channel
            if not channel.permissions_for(ctx.guild.me).send_messages:
                await ctx.respond(
                    embed=ErrorEmbed(
                        f"I don't have permission to send messages in {channel.mention}."
                    ),
                    ephemeral=True,
                )
                return

            # Create embed and view with button (persistent with guild_id)
            embed = OpenTicketEmbed()
            view = OpenTicketView(guild_id=ctx.guild.id)

            # Send the message with button to the current channel
            await channel.send(embed=embed, view=view)

            log.info(
                "Button spawned in channel",
                user_id=ctx.user.id,
                guild_id=ctx.guild.id,
                channel_id=channel.id,
                channel_name=channel.name,
            )

            await ctx.respond(
                embed=SuccessEmbed(
                    f"✅ Button message successfully sent to {channel.mention}!"
                ),
                ephemeral=True,
            )

        except discord.Forbidden as e:
            log.error(
                "Missing permissions to spawn button",
                error=str(e),
                user_id=ctx.user.id,
                guild_id=ctx.guild.id,
                channel_id=ctx.channel.id if ctx.channel else None,
            )
            await ctx.respond(
                embed=ErrorEmbed(
                    "I don't have the required permissions to send messages in this channel."
                ),
                ephemeral=True,
            )

        except discord.HTTPException as e:
            log.error(
                "HTTP error while spawning button",
                error=str(e),
                user_id=ctx.user.id,
                guild_id=ctx.guild.id,
                channel_id=ctx.channel.id if ctx.channel else None,
            )
            await ctx.respond(
                embed=ErrorEmbed(
                    "An error occurred while sending the button message. Please try again later."
                ),
                ephemeral=True,
            )

        except Exception as e:
            log.exception(
                "Unexpected error while spawning button",
                error=str(e),
                error_type=type(e).__name__,
                user_id=ctx.user.id,
                guild_id=ctx.guild.id,
                channel_id=ctx.channel.id if ctx.channel else None,
            )
            await ctx.respond(
                embed=ErrorEmbed(
                    "An unexpected error occurred. Please contact support if this persists."
                ),
                ephemeral=True,
            )


def setup(bot: Bot):
    bot.add_cog(SpawnButton(bot))
