from flask import Flask, render_template, request, jsonify, session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import stripe
import requests
from io import BytesIO
import base64
import time
import random
import json
from datetime import datetime
import os

app = Flask(__name__, template_folder='.')
app.secret_key = 'your-secret-key-here-change-in-production'

# Email configuration
EMAIL_ADDRESS = "mail@swiftvendor.store"
EMAIL_PASSWORD = "123aaa123"
SMTP_SERVER = "smtp.hostinger.com"
SMTP_PORT = 465

# Stripe configuration
stripe.api_key = "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"

# Product data
products = [
    {
        "id": 1,
        "name": "Discord Token Gen",
        "price": "$2 - $15",
        "image": "discord_token_gen.png",
        "description": "Generate Discord tokens with various subscription options",
        "options": [
            {"name": "Day Pass", "price": 2.00, "value": "day"},
            {"name": "2 Week Pass", "price": 5.00, "value": "2week"},
            {"name": "Month Pass", "price": 10.00, "value": "month"},
            {"name": "Lifetime", "price": 15.00, "value": "lifetime"}
        ]
    },
    {
        "id": 2,
        "name": "Oauth2 Boost Bot",
        "price": "$2 - $15",
        "image": "oauth2_boost_bot.png",
        "description": "Boost your server using Oauth2",
        "options": [
            {"name": "Day Pass", "price": 2.00, "value": "day"},
            {"name": "2 Week Pass", "price": 5.00, "value": "2week"},
            {"name": "Month Pass", "price": 10.00, "value": "month"},
            {"name": "Lifetime", "price": 15.00, "value": "lifetime"}
        ]
    },
    {
        "id": 3,
        "name": "Oauth2 Token Joiner",
        "price": "$2 - $15",
        "image": "oauth2_token_joiner.png",
        "description": "Join servers using Oauth2 tokens",
        "options": [
            {"name": "Day Pass", "price": 2.00, "value": "day"},
            {"name": "2 Week Pass", "price": 5.00, "value": "2week"},
            {"name": "Month Pass", "price": 10.00, "value": "month"},
            {"name": "Lifetime", "price": 15.00, "value": "lifetime"}
        ]
    },
    {
        "id": 4,
        "name": "Discord Server Cloner",
        "price": "$2 - $15",
        "image": "discord_server_cloner.png",
        "description": "Clone Discord servers with ease",
        "options": [
            {"name": "Day Pass", "price": 2.00, "value": "day"},
            {"name": "2 Week Pass", "price": 5.00, "value": "2week"},
            {"name": "Month Pass", "price": 10.00, "value": "month"},
            {"name": "Lifetime", "price": 15.00, "value": "lifetime"}
        ]
    }
]

# Function to send email
def send_email(recipient, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Function to log order to Discord (pseudo-code)
def log_order_to_discord(discord_username, email, product, option, price):
    # This would send a message to your Discord channel
    # Implementation depends on your Discord webhook setup
    print(f"Order created: {discord_username}, {email}, {product}, {option}, ${price}")

@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.route('/reviews')
def reviews():
    return render_template('reviews.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

@app.route('/initiate_payment', methods=['POST'])
def initiate_payment():
    data = request.json
    product_id = int(data['product_id'])
    option_value = data['option_value']
    email = data['email']
    discord_username = data['discord_username']
    payment_method = data['payment_method']
    
    # Find the selected product and option
    product = next((p for p in products if p['id'] == product_id), None)
    option = next((o for o in product['options'] if o['value'] == option_value), None) if product else None
    
    if not product or not option:
        return jsonify({'success': False, 'message': 'Invalid product or option'})
    
    price = option['price']
    
    # Store order in session
    session['current_order'] = {
        'product': product['name'],
        'option': option['name'],
        'price': price,
        'email': email,
        'discord_username': discord_username
    }
    
    # Create payment based on method
    if payment_method == 'stripe':
        try:
            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"{product['name']} - {option['name']}",
                        },
                        'unit_amount': int(price * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.host_url + 'success',
                cancel_url=request.host_url + 'cancel',
                metadata={
                    'product': product['name'],
                    'option': option['name'],
                    'email': email,
                    'discord_username': discord_username
                }
            )
            return jsonify({'success': True, 'redirect_url': checkout_session.url})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    elif payment_method == 'paypal':
        # For PayPal, we'll just send an email with instructions
        try:
            # Log order
            log_order_to_discord(discord_username, email, product['name'], option['name'], price)
            
            # Send email with PayPal instructions
            subject = "Swift Vendor - PayPal Payment Instructions"
            body = f"""
            <html>
            <body>
                <h2>Thank you for your order, {discord_username}!</h2>
                <p>Please send ${price} via PayPal to: jacobmoreno6541@gmail.com</p>
                <p>Include your Discord username ({discord_username}) in the notes.</p>
                <p>After payment, create a ticket with your payment proof to receive your product.</p>
                <br>
                <p><strong>Order Details:</strong></p>
                <ul>
                    <li>Product: {product['name']}</li>
                    <li>Option: {option['name']}</li>
                    <li>Price: ${price}</li>
                </ul>
                <br>
                <p>Best regards,<br>Swift Vendor Team</p>
            </body>
            </html>
            """
            
            if send_email(email, subject, body):
                return jsonify({'success': True, 'message': 'PayPal instructions sent to your email'})
            else:
                return jsonify({'success': False, 'message': 'Failed to send email instructions'})
                
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    return jsonify({'success': False, 'message': 'Invalid payment method'})

if __name__ == '__main__':
    app.run(debug=True)
