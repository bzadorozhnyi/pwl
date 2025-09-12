import asyncio
from getpass import getpass
from typing import Annotated

import typer
from pydantic import EmailStr
from sqlmodel import Field, SQLModel

import models
from core.db import AsyncSessionProxy, async_session
from core.jwt import AuthJWTService
from helpers.sqlmodel import import_models_from_package
from models.user import User
from repositories.user import get_user_repository

app = typer.Typer()


# Call the function on the models package to automatically import all SQLModel tables,
# so created_admin can work without manually importing each model.
import_models_from_package(models)


MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128


class AdminUserIn(SQLModel):
    email: EmailStr
    password: Annotated[
        str, Field(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    ]


async def create_admin(email: str, password: str):
    try:
        AdminUserIn(email=email, password=password)
    except Exception:
        raise ValueError(
            f"Invalid email or password format, credential = (email={email}, password=***)"
        )

    hashed_password = AuthJWTService().get_password_hash(password)
    admin_user = User(
        email=email,
        username=email,
        password=hashed_password,
        first_name="Admin",
        last_name="User",
        is_admin=True,
    )

    async with async_session() as session:
        proxy_session = AsyncSessionProxy(session)

        user_repo = get_user_repository(proxy_session)

        existing_user = await user_repo.get_by_identifier(email, allow_username=False)

        if existing_user:
            raise ValueError(f"User with email {email} already exists.")

        await user_repo.create(admin_user)


@app.command()
def createsuperuser():
    """
    Creates an admin user for SQLAdmin
    """
    while True:
        email = input("Email: ")
        try:
            dummy_password = (
                "A" * MIN_PASSWORD_LENGTH
            )  # Dummy password for validation ONLY
            AdminUserIn(email=email, password=dummy_password)
            break
        except Exception:
            typer.secho("Invalid email format, please try again.", fg=typer.colors.RED)

    while True:
        password = getpass("Password: ")
        try:
            AdminUserIn(email=email, password=password)
        except Exception:
            typer.secho(
                f"Invalid password, password must be between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH} characters long.",
                fg=typer.colors.RED,
            )
            continue
        break

    try:
        asyncio.run(create_admin(email, password))
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.echo(f"Admin {email} created successfully.")


if __name__ == "__main__":
    app()
