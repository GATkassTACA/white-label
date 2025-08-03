from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app, flash
import json
import os
from werkzeug.utils import secure_filename

bp = Blueprint("wizard", __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/wizard", methods=["GET", "POST"])
def create_brand():
    """Branding wizard for creating new client configurations"""
    if request.method == "POST":
        try:
            # Get form data
            client_id = request.form["client_id"].lower().strip()
            company_name = request.form["company_name"].strip()
            primary_color = request.form["primary_color"]
            secondary_color = request.form.get("secondary_color", "#6c757d")
            welcome_message = request.form["welcome_message"].strip()
            chat_placeholder = request.form.get("chat_placeholder", "Type your message...")
            footer_text = request.form.get("footer_text", f"Powered by {company_name}")
            
            # Validate required fields
            if not all([client_id, company_name, primary_color, welcome_message]):
                flash("Please fill in all required fields", "error")
                return render_template("wizard.html")
            
            # Validate client_id format (alphanumeric and underscores only)
            if not client_id.replace('_', '').isalnum():
                flash("Client ID must contain only letters, numbers, and underscores", "error")
                return render_template("wizard.html")
            
            # Handle logo upload
            logo_filename = None
            if 'logo' in request.files:
                logo_file = request.files['logo']
                if logo_file and logo_file.filename and allowed_file(logo_file.filename):
                    filename = secure_filename(logo_file.filename)
                    # Create filename with client_id prefix
                    extension = filename.rsplit('.', 1)[1].lower()
                    logo_filename = f"{client_id}-logo.{extension}"
                    
                    # Ensure static/images directory exists
                    logo_dir = os.path.join(current_app.root_path, '..', 'static', 'images')
                    os.makedirs(logo_dir, exist_ok=True)
                    
                    logo_path = os.path.join(logo_dir, logo_filename)
                    logo_file.save(logo_path)
                    
                    logo_url = f"static/images/{logo_filename}"
                else:
                    logo_url = f"static/images/{client_id}-logo.svg"  # Default to SVG placeholder
            else:
                logo_url = f"static/images/{client_id}-logo.svg"  # Default to SVG placeholder
            
            # Create branding configuration
            branding_config = {
                "company_name": company_name,
                "primary_color": primary_color,
                "secondary_color": secondary_color,
                "logo_url": logo_url,
                "welcome_message": welcome_message,
                "chat_placeholder": chat_placeholder,
                "footer_text": footer_text,
                "features": {
                    "real_time_messaging": True,
                    "file_sharing": request.form.get("file_sharing") == "on",
                    "voice_calls": request.form.get("voice_calls") == "on",
                    "video_calls": request.form.get("video_calls") == "on",
                    "custom_themes": True
                },
                "limits": {
                    "max_rooms": int(request.form.get("max_rooms", 10)),
                    "max_users_per_room": int(request.form.get("max_users_per_room", 50)),
                    "message_history_days": int(request.form.get("message_history_days", 30))
                },
                "styling": {
                    "font_family": request.form.get("font_family", "Inter, sans-serif"),
                    "border_radius": request.form.get("border_radius", "8px"),
                    "box_shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
                }
            }
            
            # Load and update existing configurations
            config_path = os.path.join(current_app.root_path, 'branding', 'configs.json')
            
            # Load current configs
            try:
                with open(config_path, 'r') as f:
                    current_configs = json.load(f)
            except FileNotFoundError:
                current_configs = {}
            
            # Check if client already exists
            if client_id in current_configs:
                flash(f"Client '{client_id}' already exists. Please choose a different client ID.", "error")
                return render_template("wizard.html")
            
            # Add new client configuration
            current_configs[client_id] = branding_config
            
            # Save updated configurations
            with open(config_path, 'w') as f:
                json.dump(current_configs, f, indent=2)
            
            flash(f"Successfully created branding for '{company_name}'!", "success")
            return redirect(url_for("chat.index", client=client_id))
            
        except Exception as e:
            flash(f"Error creating branding: {str(e)}", "error")
            return render_template("wizard.html")
    
    return render_template("wizard.html")

@bp.route("/wizard/preview", methods=["POST"])
def preview_brand():
    """Preview branding configuration"""
    try:
        # Get form data for preview
        preview_config = {
            "company_name": request.form.get("company_name", "Preview Company"),
            "primary_color": request.form.get("primary_color", "#007bff"),
            "secondary_color": request.form.get("secondary_color", "#6c757d"),
            "welcome_message": request.form.get("welcome_message", "Welcome to our chat!"),
            "chat_placeholder": request.form.get("chat_placeholder", "Type your message..."),
            "footer_text": request.form.get("footer_text", "Powered by Preview Company"),
        }
        
        return jsonify({"success": True, "config": preview_config})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@bp.route("/wizard/validate-client-id", methods=["POST"])
def validate_client_id():
    """Validate if client ID is available"""
    try:
        client_id = request.json.get("client_id", "").lower().strip()
        
        if not client_id:
            return jsonify({"valid": False, "message": "Client ID is required"})
        
        # Check format
        if not client_id.replace('_', '').isalnum():
            return jsonify({"valid": False, "message": "Client ID must contain only letters, numbers, and underscores"})
        
        # Check if already exists
        config_path = os.path.join(current_app.root_path, 'branding', 'configs.json')
        try:
            with open(config_path, 'r') as f:
                current_configs = json.load(f)
            
            if client_id in current_configs:
                return jsonify({"valid": False, "message": "Client ID already exists"})
        except FileNotFoundError:
            pass  # File doesn't exist yet, that's ok
        
        return jsonify({"valid": True, "message": "Client ID is available"})
        
    except Exception as e:
        return jsonify({"valid": False, "message": str(e)})
