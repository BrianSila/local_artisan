import click
from flask import current_app
from flask.cli import with_appcontext
from app.extensions import db
from app.accounts.models import User

# Import models 
from app.locations.models import County, SubCounty
from app.services.models import Category 

from app.seeds.counties_data import KENYA_COUNTIES
from app.seeds.sub_counties_data import MAJOR_SUB_COUNTIES
from app.seeds.categories_data import PLATFORM_CATEGORIES


def seed_major_subcounties() -> int:
    counties_by_code = {county.code: county for county in County.query.all()}
    missing_codes = sorted({item["county_code"] for item in MAJOR_SUB_COUNTIES} - counties_by_code.keys())
    if missing_codes:
        raise click.ClickException(
            f"Seed counties before subcounties; missing county codes: {missing_codes}"
        )

    added = 0
    for item in MAJOR_SUB_COUNTIES:
        county = counties_by_code[item["county_code"]]
        existing = SubCounty.query.filter_by(county_id=county.id, name=item["name"]).first()
        if existing is None:
            subcounty = SubCounty()
            subcounty.county_id = county.id
            subcounty.name = item["name"]
            db.session.add(subcounty)
            added += 1

    db.session.commit()
    return added

@click.command("db-seed-all")
@with_appcontext
def seed_all_command():
    """🚀 Master Command: Seeds the entire database ecosystem at once."""
    click.echo("==== 🛠️ Starting Centralized Database Seeding ====")
    
    # 1. Seed Counties
    click.echo("-> Seeding 47 Kenyan Counties...")
    counties_added = 0
    for county_data in KENYA_COUNTIES:
        existing = County.query.filter_by(code=county_data["code"]).first()
        if not existing:
            db.session.add(County(code=county_data["code"], name=county_data["name"]))
            counties_added += 1
    
    db.session.commit()
    click.echo(f"   Success: {counties_added} new counties verified/saved.")

    # 2. Seed one primary subcounty for each county.
    subcounties_added = seed_major_subcounties()
    click.echo(f"   Success: {subcounties_added} new major subcounties saved.")

    # 3. Seed Macro Service Categories 
    click.echo("-> Seeding baseline service categories...")
    categories_added = 0
    for cat in PLATFORM_CATEGORIES:
        if not Category.query.filter_by(slug=cat["slug"]).first():
            db.session.add(Category(name=cat["name"], slug=cat["slug"], icon_name=cat["icon_name"]))
            categories_added += 1
    db.session.commit()
    click.echo(f"   Success: {categories_added} service categories saved.")


    click.echo("==== 🎉 Master Database Seeding Completed Successfully! ====")


@click.command("db-seed-subcounties")
@with_appcontext
def seed_subcounties_command():
    """Seed one primary subcounty for every already-seeded county."""
    added = seed_major_subcounties()
    click.echo(f"Seeded {added} new major subcounties.")


@click.command("db-seed-admin")
@click.option("--email", envvar="ADMIN_EMAIL")
@click.option("--name", envvar="ADMIN_NAME")
@click.option(
    "--password",
    envvar="ADMIN_PASSWORD",
    hide_input=True,
)
@with_appcontext
def seed_admin_command(email, name, password):
    """Create the initial administrator with dev defaults or prompted credentials."""
    allow_weak_password = bool(current_app.config.get("ALLOW_WEAK_ADMIN_SEED", False))
    email = email or current_app.config.get("DEFAULT_ADMIN_EMAIL")
    name = name or current_app.config.get("DEFAULT_ADMIN_NAME") or "Platform Administrator"
    password = password or current_app.config.get("DEFAULT_ADMIN_PASSWORD")

    if email is None:
        email = click.prompt("Admin email")
    if password is None:
        password = click.prompt("Admin password", hide_input=True, confirmation_prompt=True)

    email = email.strip().lower()
    if "@" not in email or any(character.isspace() for character in email):
        raise click.ClickException("Enter a valid admin email address.")
    min_password_length = 8 if allow_weak_password else 12
    if not min_password_length <= len(password) <= 50:
        raise click.ClickException(
            f"Admin password must be between {min_password_length} and 50 characters."
        )

    existing_user = User.query.filter_by(email=email).first()
    if existing_user is not None:
        if existing_user.role == "admin":
            click.echo(f"Admin account {email} already exists; no changes made.")
            return
        raise click.ClickException(
            f"An account with {email} already exists as role '{existing_user.role}'. "
            "Use a different admin email; this command will not promote an existing account."
        )

    admin = User()
    admin.name = name.strip() or "Platform Administrator"
    admin.email = email
    admin.role = "admin"
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    click.echo(f"Created admin account {email}.")
    if allow_weak_password and password == "Test123!":
        click.secho(
            "Warning: the development admin uses the public test password. "
            "Do not expose this account or database outside local development.",
            fg="yellow",
        )