from flask import Flask, jsonify
from .config import config_by_name
from .extensions import db, migrate, jwt, cache, cors


def create_app(config_name="development", test_config=None):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    if test_config:
        app.config.update(test_config)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cache.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config.get("ALLOWED_ORIGINS", "*")}})

    #Import Models
    from app.locations.models import County
    from app.locations.models import SubCounty
    from app.accounts.models import User
    from app.accounts.models import ArtisanProfile, SavedArtisan
    from app.services.models import Category
    from app.services.models import ArtisanService
    from app.bookings.models import AvailabilitySlot, Booking
    from app.operations.models import MpesaTransaction
    from app.operations.models import Review 
    from app.operations.models import Dispute
    
    # Register blueprints
    from app.locations.routes import locations_bp
    from app.accounts.routes import auth_bp
    from app.artisan.routes import artisan_bp
    from app.services.routes import services_bp
    from app.bookings.routes import bookings_bp
    from app.operations.routes import operations_bp
    from app.admin.routes import admin_bp
    
    app.register_blueprint(locations_bp, url_prefix="/api/locations")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(artisan_bp, url_prefix="/api/artisan")
    app.register_blueprint(services_bp, url_prefix="/api/marketplace")
    app.register_blueprint(bookings_bp, url_prefix="/api/bookings")
    app.register_blueprint(operations_bp, url_prefix="/api/operations")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    
    # Register Custom CLI Terminal Commands
    from app.seeds.commands import seed_admin_command, seed_all_command, seed_subcounties_command
    app.cli.add_command(seed_all_command)
    app.cli.add_command(seed_admin_command)
    app.cli.add_command(seed_subcounties_command)
    
    
    # Error handlers
    from .common.errors import register_error_handlers
    register_error_handlers(app)

    @app.get("/")
    def home():
        return jsonify(status="ok",
                        msg="Local artisan api is running")
    
    @app.get("/health")
    def health():
        return jsonify(status="ok")

    return app