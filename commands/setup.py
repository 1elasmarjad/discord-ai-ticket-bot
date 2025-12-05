import discord
from discord import Bot, ApplicationContext, CategoryChannel, Member, Option, Role
from discord.ext.commands import Cog
from sqlmodel import Session

from embeds.responses import ErrorEmbed
from database import engine, Guild
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
        category_name: Option(
            str,
            description="The custom name of the category for tickets",
            default="Tickets",
        ),
        ticket_admin_role: Option(
            Role,
            description="The role that should have access to the category",
            default=None,
        ),
    ):
        try:
            # Check if guild already exists in database
            with Session(engine) as session:
                existing_guild = session.get(Guild, ctx.guild.id)
                if existing_guild is not None:
                    await ctx.respond(
                        embed=ErrorEmbed(
                            "This server has already been set up. Please use other commands to manage your ticket system."
                        ),
                        ephemeral=True,
                    )
                    return

            bot_member: Member | None = ctx.guild.get_member(self.bot.user.id)

            if not bot_member:
                await ctx.respond(
                    embed=ErrorEmbed(
                        "I'm not in the server. Please add me to the server and try again."
                    ),
                    ephemeral=True,
                )
                return

            category: CategoryChannel = await ctx.guild.create_category(category_name)

            # Give the bot full permissions to manage the category
            await category.set_permissions(
                bot_member,
                view_channel=True,
                manage_channels=True,
                manage_permissions=True,
                send_messages=True,
                read_messages=True,
                read_message_history=True,
                attach_files=True,
                embed_links=True,
            )

            # Deny @everyone from viewing the category
            everyone_role: Role = ctx.guild.default_role
            await category.set_permissions(
                everyone_role,
                view_channel=False,
            )

            # Allow the specified role to view the category
            if ticket_admin_role:
                await category.set_permissions(
                    ticket_admin_role,
                    view_channel=True,
                    send_messages=True,
                    read_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True,
                )

            # Save the guild and category ID to the database
            with Session(engine) as session:
                guild = Guild(id=ctx.guild.id, category_channel_id=category.id)
                session.add(guild)
                session.commit()
                session.refresh(guild)

            log.info(
                "Ticket category setup completed successfully",
                user_id=ctx.user.id,
                guild_id=ctx.guild.id,
                category_id=category.id,
                category_name=category_name,
                ticket_admin_role_id=ticket_admin_role.id
                if ticket_admin_role
                else None,
            )

            await ctx.respond(
                embed=discord.Embed(
                    title="✅ Tickets Setup Complete",
                    description=f"The **{category_name}** category has been created with proper permissions.",
                    color=discord.Color.green(),
                ),
                ephemeral=True,
            )

        except discord.Forbidden as e:
            log.error(
                "Missing permissions to setup ticket category",
                error=str(e),
                user_id=ctx.user.id,
                guild_id=ctx.guild.id,
                category_name=category_name,
            )
            await ctx.respond(
                embed=ErrorEmbed(
                    "I don't have the required permissions. Please ensure I have 'Manage Channels' and 'Manage Permissions' permissions."
                ),
                ephemeral=True,
            )

        except discord.NotFound as e:
            log.error(
                "Resource not found during ticket category setup",
                error=str(e),
                user_id=ctx.user.id,
                guild_id=ctx.guild.id,
                category_name=category_name,
            )
            await ctx.respond(
                embed=ErrorEmbed(
                    "A required resource was not found. Please try again."
                ),
                ephemeral=True,
            )

        except discord.HTTPException as e:
            log.error(
                "HTTP error during ticket category setup",
                error=str(e),
                status_code=e.status if hasattr(e, "status") else None,
                user_id=ctx.user.id,
                guild_id=ctx.guild.id,
                category_name=category_name,
            )
            await ctx.respond(
                embed=ErrorEmbed(
                    "An error occurred while setting up the ticket category. Please try again later."
                ),
                ephemeral=True,
            )

        except discord.InvalidArgument as e:
            log.error(
                "Invalid argument during ticket category setup",
                error=str(e),
                user_id=ctx.user.id,
                guild_id=ctx.guild.id,
                category_name=category_name,
                ticket_admin_role_id=ticket_admin_role.id
                if ticket_admin_role
                else None,
            )
            await ctx.respond(
                embed=ErrorEmbed(
                    "Invalid configuration provided. Please check your settings and try again."
                ),
                ephemeral=True,
            )

        except Exception as e:
            log.exception(
                "Unexpected error during ticket category setup",
                error=str(e),
                error_type=type(e).__name__,
                user_id=ctx.user.id,
                guild_id=ctx.guild.id,
                category_name=category_name,
            )
            await ctx.respond(
                embed=ErrorEmbed(
                    "An unexpected error occurred. Please contact support if this persists."
                ),
                ephemeral=True,
            )


def setup(bot: Bot):
    bot.add_cog(Setup(bot))
