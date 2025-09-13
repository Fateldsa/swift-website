from flask import Flask, render_template, request, jsonify, session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import stripe
import paypalrestsdk
import requests
from io import BytesIO
import base64
import time
import random
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Email configuration
EMAIL_ADDRESS = "mail@swiftvendor.store"
EMAIL_PASSWORD = "123aaa123"
SMTP_SERVER = "smtp.hostinger.com"
SMTP_PORT = 465

# Stripe configuration
stripe.api_key = "your-stripe-secret-key"  # Replace with your Stripe secret key

# PayPal configuration
paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": "your-paypal-client-id",
    "client_secret": "your-paypal-secret-key"
})

# Product data
products = [
    {
        "id": 1,
        "name": "Discord Token Gen",
        "price": "$2 - $15",
        "image": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMDAgMjAwIiBmaWxsPSJub25lIj48Y2lyY2xlIGN4PSIxMDAiIGN5PSIxMDAiIHI9IjEwMCIgZmlsbD0iIzcyODlEQUIiLz48cGF0aCBkPSJNNjUgNjVIMTM1VjEzNUg2NVY2NVoiIGZpbGw9IndoaXRlIi8+PC9zdmc+",
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
        "price": "$5 - $20",
        "image": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMDAgMjAwIiBmaWxsPSJub25lIj48Y2lyY2xlIGN4PSIxMDAiIGN5PSIxMDAiIHI9IjEwMCIgZmlsbD0iIzU4YTU3MCIvPjxwYXRoIGQ9Ik03MCA3MEgxMzBWMTMwSDcwVjcwWiIgZmlsbD0id2hpdGUiLz48L3N2Zz4=",
        "description": "Boost your server using Oauth2",
        "options": [
            {"name": "Basic", "price": 5.00, "value": "basic"},
            {"name": "Premium", "price": 10.00, "value": "premium"},
            {"name": "Ultimate", "price": 15.00, "value": "ultimate"},
            {"name": "Lifetime", "price": 20.00, "value": "lifetime"}
        ]
    },
    {
        "id": 3,
        "name": "Oauth2 Token Joiner",
        "price": "$3 - $12",
        "image": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMDAgMjAwIiBmaWxsPSJub25lIj48Y2lyY2xlIGN4PSIxMDAiIGN5PSIxMDAiIHI9IjEwMCIgZmlsbD0iI0YyQzJBQyIvPjxwYXRoIGQ9Ik03MCA3MEgxMzBWMTMwSDcwVjcwWiIgZmlsbD0id2hpdGUiLz48L3N2Zz4=",
        "description": "Join servers using Oauth2 tokens",
        "options": [
            {"name": "Day Pass", "price": 3.00, "value": "day"},
            {"name": "Week Pass", "price": 5.00, "value": "week"},
            {"name": "Month Pass", "price": 8.00, "value": "month"},
            {"name": "Lifetime", "price": 12.00, "value": "lifetime"}
        ]
    },
    {
        "id": 4,
        "name": "Discord Server Cloner",
        "price": "$10 - $25",
        "image": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMDAgMjAwIiBmaWxsPSJub25lIj48Y2lyY2xlIGN4PSIxMDAiIGN5PSIxMDAiIHI9IjEwMCIgZmlsbD0iIzkzNEE0QyIvPjxwYXRoIGQ9Ik03MCA3MEgxMzBWMTMwSDcwVjcwWiIgZmlsbD0id2hpdGUiLz48L3N2Zz4=",
        "description": "Clone Discord servers with ease",
        "options": [
            {"name": "Basic", "price": 10.00, "value": "basic"},
            {"name": "Premium", "price": 15.00, "value": "premium"},
            {"name": "Ultimate", "price": 20.00, "value": "ultimate"},
            {"name": "Lifetime", "price": 25.00, "value": "lifetime"}
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
    return render_template_string(HTML_TEMPLATE, products=products)

@app.route('/reviews')
def reviews():
    return render_template_string(REVIEWS_TEMPLATE)

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
                success_url=request.host_url + 'payment_success',
                cancel_url=request.host_url + 'payment_cancel',
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
        try:
            # Create PayPal payment
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": request.host_url + 'payment_success',
                    "cancel_url": request.host_url + 'payment_cancel'
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": f"{product['name']} - {option['name']}",
                            "price": str(price),
                            "currency": "USD",
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": str(price),
                        "currency": "USD"
                    },
                    "description": f"Purchase of {product['name']} - {option['name']}"
                }]
            })
            
            if payment.create():
                # Log order
                log_order_to_discord(discord_username, email, product['name'], option['name'], price)
                
                # Find approval URL
                for link in payment.links:
                    if link.rel == "approval_url":
                        return jsonify({'success': True, 'redirect_url': link.href})
            
            return jsonify({'success': False, 'message': 'Failed to create PayPal payment'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    return jsonify({'success': False, 'message': 'Invalid payment method'})

@app.route('/payment_success')
def payment_success():
    order = session.get('current_order', {})
    if order:
        # Send confirmation email
        subject = "Your Order Confirmation - Swift Vendor"
        body = f"""
        <html>
        <body>
            <h2>Thank you for your purchase, {order['discord_username']}!</h2>
            <p>Your order details:</p>
            <ul>
                <li>Product: {order['product']}</li>
                <li>Option: {order['option']}</li>
                <li>Price: ${order['price']}</li>
            </ul>
            <p>We will process your order shortly.</p>
            <br>
            <p>Best regards,<br>Swift Vendor Team</p>
        </body>
        </html>
        """
        send_email(order['email'], subject, body)
    
    return render_template_string(SUCCESS_TEMPLATE)

@app.route('/payment_cancel')
def payment_cancel():
    return render_template_string(CANCEL_TEMPLATE)

# HTML Templates with space theme and effects
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Swift Vendor Store</title>
    <style>
        :root {
            --primary: #8a2be2;
            --secondary: #4b0082;
            --dark: #0a0a1a;
            --light: #f0f0f0;
            --accent: #9370db;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Arial', sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, var(--dark) 0%, #1a1a2e 100%);
            color: var(--light);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }
        
        #particles-js {
            position: fixed;
            width: 100%;
            height: 100%;
            z-index: -1;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            padding: 30px 0;
        }
        
        .logo {
            font-size: 3rem;
            font-weight: bold;
            background: linear-gradient(45deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            text-shadow: 0 0 10px rgba(138, 43, 226, 0.5);
        }
        
        .tagline {
            font-size: 1.2rem;
            opacity: 0.8;
            margin-bottom: 30px;
        }
        
        .products-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }
        
        .product-card {
            background: rgba(20, 20, 40, 0.7);
            border-radius: 15px;
            overflow: hidden;
            transition: transform 0.3s, box-shadow 0.3s;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(138, 43, 226, 0.3);
        }
        
        .product-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 10px 30px rgba(138, 43, 226, 0.3);
        }
        
        .product-image {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-bottom: 2px solid var(--primary);
        }
        
        .product-info {
            padding: 20px;
        }
        
        .product-name {
            font-size: 1.5rem;
            margin-bottom: 10px;
            color: var(--accent);
        }
        
        .product-price {
            font-size: 1.2rem;
            color: #ffd700;
            margin-bottom: 15px;
        }
        
        .product-description {
            margin-bottom: 20px;
            opacity: 0.8;
            font-size: 0.9rem;
        }
        
        .buy-btn {
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 50px;
            cursor: pointer;
            font-weight: bold;
            width: 100%;
            transition: all 0.3s;
        }
        
        .buy-btn:hover {
            background: linear-gradient(45deg, var(--secondary), var(--primary));
            box-shadow: 0 0 15px rgba(138, 43, 226, 0.7);
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(5px);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        
        .modal-content {
            background: rgba(30, 30, 60, 0.9);
            padding: 30px;
            border-radius: 15px;
            width: 90%;
            max-width: 500px;
            border: 1px solid var(--primary);
            box-shadow: 0 0 30px rgba(138, 43, 226, 0.5);
        }
        
        .close-modal {
            float: right;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--accent);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid rgba(138, 43, 226, 0.5);
            background: rgba(10, 10, 30, 0.7);
            color: white;
        }
        
        .options-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .option-btn {
            padding: 10px;
            text-align: center;
            background: rgba(20, 20, 40, 0.7);
            border: 1px solid rgba(138, 43, 226, 0.3);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .option-btn.selected {
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            border-color: var(--accent);
            box-shadow: 0 0 10px rgba(138, 43, 226, 0.5);
        }
        
        .payment-options {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .payment-option {
            flex: 1;
            text-align: center;
            padding: 15px;
            background: rgba(20, 20, 40, 0.7);
            border: 1px solid rgba(138, 43, 226, 0.3);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .payment-option.selected {
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            border-color: var(--accent);
            box-shadow: 0 0 10px rgba(138, 43, 226, 0.5);
        }
        
        .submit-payment {
            background: linear-gradient(45deg, #00cc66, #00b359);
            color: white;
            border: none;
            padding: 15px;
            border-radius: 50px;
            cursor: pointer;
            font-weight: bold;
            width: 100%;
            transition: all 0.3s;
        }
        
        .submit-payment:hover {
            background: linear-gradient(45deg, #00b359, #00cc66);
            box-shadow: 0 0 15px rgba(0, 204, 102, 0.7);
        }
        
        .nav {
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
        }
        
        .nav a {
            color: var(--accent);
            text-decoration: none;
            margin: 0 15px;
            padding: 10px 20px;
            border-radius: 50px;
            transition: all 0.3s;
        }
        
        .nav a:hover {
            background: rgba(138, 43, 226, 0.2);
        }
        
        .video-container {
            margin: 40px 0;
            text-align: center;
        }
        
        .video-placeholder {
            width: 100%;
            max-width: 560px;
            height: 315px;
            background: rgba(20, 20, 40, 0.7);
            margin: 0 auto;
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 15px;
            border: 1px solid rgba(138, 43, 226, 0.3);
        }
        
        footer {
            text-align: center;
            padding: 30px 0;
            margin-top: 50px;
            opacity: 0.7;
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            .products-grid {
                grid-template-columns: 1fr;
            }
            
            .options-grid {
                grid-template-columns: 1fr;
            }
            
            .payment-options {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div id="particles-js"></div>
    
    <div class="container">
        <header>
            <div class="logo">SWIFT VENDOR</div>
            <div class="tagline">Premium Discord Tools & Services</div>
        </header>
        
        <div class="nav">
            <a href="/">Home</a>
            <a href="/reviews">Reviews</a>
        </div>
        
        <div class="video-container">
            <div class="video-placeholder">
                <p>YouTube Video Embed Here</p>
            </div>
        </div>
        
        <div class="products-grid">
            {% for product in products %}
            <div class="product-card">
                <img src="{{ product.image }}" alt="{{ product.name }}" class="product-image">
                <div class="product-info">
                    <h3 class="product-name">{{ product.name }}</h3>
                    <div class="product-price">{{ product.price }}</div>
                    <p class="product-description">{{ product.description }}</p>
                    <button class="buy-btn" onclick="openModal({{ product.id }})">Buy Now</button>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <div class="modal" id="paymentModal">
        <div class="modal-content">
            <span class="close-modal" onclick="closeModal()">&times;</span>
            <h2>Complete Your Purchase</h2>
            <form id="paymentForm">
                <input type="hidden" id="productId">
                
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" required>
                </div>
                
                <div class="form-group">
                    <label for="discordUsername">Discord Username</label>
                    <input type="text" id="discordUsername" required>
                </div>
                
                <div class="form-group">
                    <label>Select Option</label>
                    <div class="options-grid" id="optionsContainer">
                        <!-- Options will be inserted here by JavaScript -->
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Payment Method</label>
                    <div class="payment-options">
                        <div class="payment-option" data-method="stripe" onclick="selectPayment(this)">
                            Credit Card
                        </div>
                        <div class="payment-option" data-method="paypal" onclick="selectPayment(this)">
                            PayPal
                        </div>
                    </div>
                </div>
                
                <button type="submit" class="submit-payment">Proceed to Payment</button>
            </form>
        </div>
    </div>
    
    <footer>
        <p>&copy; 2023 Swift Vendor Store. All rights reserved.</p>
    </footer>

    <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
    <script>
        // Initialize particles.js
        particlesJS('particles-js', {
            particles: {
                number: { value: 80, density: { enable: true, value_area: 800 } },
                color: { value: "#8a2be2" },
                shape: { type: "circle" },
                opacity: { value: 0.5, random: true },
                size: { value: 3, random: true },
                line_linked: {
                    enable: true,
                    distance: 150,
                    color: "#9370db",
                    opacity: 0.4,
                    width: 1
                },
                move: {
                    enable: true,
                    speed: 2,
                    direction: "none",
                    random: true,
                    straight: false,
                    out_mode: "out",
                    bounce: false
                }
            },
            interactivity: {
                detect_on: "canvas",
                events: {
                    onhover: { enable: true, mode: "repulse" },
                    onclick: { enable: true, mode: "push" },
                    resize: true
                }
            },
            retina_detect: true
        });
        
        // Product data from Flask
        const products = {{ products | tojson }};
        
        let selectedOption = null;
        let selectedPaymentMethod = null;
        
        function openModal(productId) {
            document.getElementById('productId').value = productId;
            const product = products.find(p => p.id === productId);
            
            // Populate options
            const optionsContainer = document.getElementById('optionsContainer');
            optionsContainer.innerHTML = '';
            
            product.options.forEach(option => {
                const optionEl = document.createElement('div');
                optionEl.className = 'option-btn';
                optionEl.dataset.value = option.value;
                optionEl.innerHTML = `
                    <strong>${option.name}</strong><br>
                    $${option.price.toFixed(2)}
                `;
                optionEl.onclick = () => selectOption(optionEl, option);
                optionsContainer.appendChild(optionEl);
            });
            
            // Reset form
            document.getElementById('email').value = '';
            document.getElementById('discordUsername').value = '';
            selectedOption = null;
            selectedPaymentMethod = null;
            
            // Clear selections
            document.querySelectorAll('.option-btn').forEach(btn => btn.classList.remove('selected'));
            document.querySelectorAll('.payment-option').forEach(btn => btn.classList.remove('selected'));
            
            // Show modal
            document.getElementById('paymentModal').style.display = 'flex';
        }
        
        function closeModal() {
            document.getElementById('paymentModal').style.display = 'none';
        }
        
        function selectOption(element, option) {
            document.querySelectorAll('.option-btn').forEach(btn => btn.classList.remove('selected'));
            element.classList.add('selected');
            selectedOption = option;
        }
        
        function selectPayment(element) {
            document.querySelectorAll('.payment-option').forEach(btn => btn.classList.remove('selected'));
            element.classList.add('selected');
            selectedPaymentMethod = element.dataset.method;
        }
        
        document.getElementById('paymentForm').onsubmit = async function(e) {
            e.preventDefault();
            
            if (!selectedOption) {
                alert('Please select an option');
                return;
            }
            
            if (!selectedPaymentMethod) {
                alert('Please select a payment method');
                return;
            }
            
            const email = document.getElementById('email').value;
            const discordUsername = document.getElementById('discordUsername').value;
            const productId = document.getElementById('productId').value;
            
            const response = await fetch('/initiate_payment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    product_id: parseInt(productId),
                    option_value: selectedOption.value,
                    email: email,
                    discord_username: discordUsername,
                    payment_method: selectedPaymentMethod
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                window.location.href = result.redirect_url;
            } else {
                alert('Error: ' + result.message);
            }
        };
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            if (event.target === document.getElementById('paymentModal')) {
                closeModal();
            }
        };
    </script>
</body>
</html>
"""

REVIEWS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reviews - Swift Vendor Store</title>
    <style>
        /* Same styles as index page */
        :root {
            --primary: #8a2be2;
            --secondary: #4b0082;
            --dark: #0a0a1a;
            --light: #f0f0f0;
            --accent: #9370db;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Arial', sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, var(--dark) 0%, #1a1a2e 100%);
            color: var(--light);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }
        
        #particles-js {
            position: fixed;
            width: 100%;
            height: 100%;
            z-index: -1;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            padding: 30px 0;
        }
        
        .logo {
            font-size: 3rem;
            font-weight: bold;
            background: linear-gradient(45deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            text-shadow: 0 0 10px rgba(138, 43, 226, 0.5);
        }
        
        .tagline {
            font-size: 1.2rem;
            opacity: 0.8;
            margin-bottom: 30px;
        }
        
        .nav {
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
        }
        
        .nav a {
            color: var(--accent);
            text-decoration: none;
            margin: 0 15px;
            padding: 10px 20px;
            border-radius: 50px;
            transition: all 0.3s;
        }
        
        .nav a:hover {
            background: rgba(138, 43, 226, 0.2);
        }
        
        .reviews-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }
        
        .review-card {
            background: rgba(20, 20, 40, 0.7);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(138, 43, 226, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .review-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .user-avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            object-fit: cover;
            margin-right: 15px;
            border: 2px solid var(--primary);
        }
        
        .user-info {
            flex: 1;
        }
        
        .username {
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        .badge {
            display: inline-block;
            background: linear-gradient(45deg, #00cc66, #00b359);
            color: white;
            padding: 3px 10px;
            border-radius: 50px;
            font-size: 0.8rem;
            margin-top: 5px;
        }
        
        .review-content {
            line-height: 1.6;
        }
        
        .review-date {
            margin-top: 15px;
            font-size: 0.8rem;
            opacity: 0.7;
        }
        
        .stats {
            text-align: center;
            margin: 40px 0;
            font-size: 1.5rem;
        }
        
        .count {
            font-weight: bold;
            color: var(--accent);
        }
        
        footer {
            text-align: center;
            padding: 30px 0;
            margin-top: 50px;
            opacity: 0.7;
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            .reviews-container {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div id="particles-js"></div>
    
    <div class="container">
        <header>
            <div class="logo">SWIFT VENDOR</div>
            <div class="tagline">What Our Customers Say</div>
        </header>
        
        <div class="nav">
            <a href="/">Home</a>
            <a href="/reviews">Reviews</a>
        </div>
        
        <div class="stats">
            <span class="count">1274</span> Happy Customers & Counting!
        </div>
        
        <div class="reviews-container">
            <div class="review-card">
                <div class="review-header">
                    <img src="https://cdn.discordapp.com/avatars/123456789012345678/abcdefghijklmnopqrstuvwxyz.webp" alt="User" class="user-avatar">
                    <div class="user-info">
                        <div class="username">JohnDoe#1234</div>
                        <div class="badge">Paid</div>
                    </div>
                </div>
                <div class="review-content">
                    Amazing service! The token gen worked perfectly and I got exactly what I paid for. Will definitely purchase again!
                </div>
                <div class="review-date">September 12, 2023</div>
            </div>
            
            <div class="review-card">
                <div class="review-header">
                    <img src="https://cdn.discordapp.com/avatars/234567890123456789/bcdefghijklmnopqrstuvwxyza.webp" alt="User" class="user-avatar">
                    <div class="user-info">
                        <div class="username">JaneSmith#4567</div>
                        <div class="badge">Paid</div>
                    </div>
                </div>
                <div class="review-content">
                    The server cloner is incredible! Saved me so much time and effort. Support was helpful when I had questions too.
                </div>
                <div class="review-date">September 10, 2023</div>
            </div>
            
            <div class="review-card">
                <div class="review-header">
                    <img src="https://cdn.discordapp.com/avatars/345678901234567890/cdefghijklmnopqrstuvwxyzab.webp" alt="User" class="user-avatar">
                    <div class="user-info">
                        <div class="username">MikeJohnson#7890</div>
                        <div class="badge">Paid</div>
                    </div>
                </div>
                <div class="review-content">
                    Fast delivery and quality product. The Oauth2 boost bot works like a charm. Highly recommend!
                </div>
                <div class="review-date">September 8, 2023</div>
            </div>
            
            <div class="review-card">
                <div class="review-header">
                    <img src="https://cdn.discordapp.com/avatars/456789012345678901/defghijklmnopqrstuvwxyzabc.webp" alt="User" class="user-avatar">
                    <div class="user-info">
                        <div class="username">SarahWilliams#0123</div>
                        <div class="badge">Paid</div>
                    </div>
                </div>
                <div class="review-content">
                    Purchased the lifetime pass for token gen and it's been worth every penny. Constant updates and great functionality.
                </div>
                <div class="review-date">September 5, 2023</div>
            </div>
            
            <div class="review-card">
                <div class="review-header">
                    <img src="https://cdn.discordapp.com/avatars/567890123456789012/efghijklmnopqrstuvwxyzabcd.webp" alt="User" class="user-avatar">
                    <div class="user-info">
                        <div class="username">AlexBrown#3456</div>
                        <div class="badge">Paid</div>
                    </div>
                </div>
                <div class="review-content">
                    The token joiner works flawlessly. Setup was easy and the results were exactly as advertised. 5 stars!
                </div>
                <div class="review-date">September 3, 2023</div>
            </div>
            
            <div class="review-card">
                <div class="review-header">
                    <img src="https://cdn.discordapp.com/avatars/678901234567890123/fghijklmnopqrstuvwxyzabcde.webp" alt="User" class="user-avatar">
                    <div class="user-info">
                        <div class="username">EmilyDavis#6789</div>
                        <div class="badge">Paid</div>
                    </div>
                </div>
                <div class="review-content">
                    I was hesitant at first but decided to try the month pass. So glad I did! The tools are premium quality and customer support is top-notch.
                </div>
                <div class="review-date">August 30, 2023</div>
            </div>
        </div>
    </div>
    
    <footer>
        <p>&copy; 2023 Swift Vendor Store. All rights reserved.</p>
    </footer>

    <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
    <script>
        // Initialize particles.js
        particlesJS('particles-js', {
            particles: {
                number: { value: 80, density: { enable: true, value_area: 800 } },
                color: { value: "#8a2be2" },
                shape: { type: "circle" },
                opacity: { value: 0.5, random: true },
                size: { value: 3, random: true },
                line_linked: {
                    enable: true,
                    distance: 150,
                    color: "#9370db",
                    opacity: 0.4,
                    width: 1
                },
                move: {
                    enable: true,
                    speed: 2,
                    direction: "none",
                    random: true,
                    straight: false,
                    out_mode: "out",
                    bounce: false
                }
            },
            interactivity: {
                detect_on: "canvas",
                events: {
                    onhover: { enable: true, mode: "repulse" },
                    onclick: { enable: true, mode: "push" },
                    resize: true
                }
            },
            retina_detect: true
        });
    </script>
</body>
</html>
"""

SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payment Successful - Swift Vendor Store</title>
    <style>
        /* Same styles as index page */
        :root {
            --primary: #8a2be2;
            --secondary: #4b0082;
            --dark: #0a0a1a;
            --light: #f0f0f0;
            --accent: #9370db;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Arial', sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, var(--dark) 0%, #1a1a2e 100%);
            color: var(--light);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        #particles-js {
            position: fixed;
            width: 100%;
            height: 100%;
            z-index: -1;
        }
        
        .success-container {
            text-align: center;
            background: rgba(20, 20, 40, 0.7);
            padding: 40px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(138, 43, 226, 0.3);
            max-width: 500px;
            width: 90%;
        }
        
        .checkmark {
            color: #00cc66;
            font-size: 4rem;
            margin-bottom: 20px;
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 20px;
            background: linear-gradient(45deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        p {
            margin-bottom: 30px;
            line-height: 1.6;
        }
        
        .btn {
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 50px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
        }
        
        .btn:hover {
            background: linear-gradient(45deg, var(--secondary), var(--primary));
            box-shadow: 0 0 15px rgba(138, 43, 226, 0.7);
        }
    </style>
</head>
<body>
    <div id="particles-js"></div>
    
    <div class="success-container">
        <div class="checkmark">✓</div>
        <h1>Payment Successful!</h1>
        <p>Thank you for your purchase. You will receive an email confirmation shortly with your order details.</p>
        <a href="/" class="btn">Return to Home</a>
    </div>

    <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
    <script>
        // Initialize particles.js
        particlesJS('particles-js', {
            particles: {
                number: { value: 80, density: { enable: true, value_area: 800 } },
                color: { value: "#8a2be2" },
                shape: { type: "circle" },
                opacity: { value: 0.5, random: true },
                size: { value: 3, random: true },
                line_linked: {
                    enable: true,
                    distance: 150,
                    color: "#9370db",
                    opacity: 0.4,
                    width: 1
                },
                move: {
                    enable: true,
                    speed: 2,
                    direction: "none",
                    random: true,
                    straight: false,
                    out_mode: "out",
                    bounce: false
                }
            },
            interactivity: {
                detect_on: "canvas",
                events: {
                    onhover: { enable: true, mode: "repulse" },
                    onclick: { enable: true, mode: "push" },
                    resize: true
                }
            },
            retina_detect: true
        });
    </script>
</body>
</html>
"""

CANCEL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payment Cancelled - Swift Vendor Store</title>
    <style>
        /* Same styles as index page */
        :root {
            --primary: #8a2be2;
            --secondary: #4b0082;
            --dark: #0a0a1a;
            --light: #f0f0f0;
            --accent: #9370db;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Arial', sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, var(--dark) 0%, #1a1a2e 100%);
            color: var(--light);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        #particles-js {
            position: fixed;
            width: 100%;
            height: 100%;
            z-index: -1;
        }
        
        .cancel-container {
            text-align: center;
            background: rgba(20, 20, 40, 0.7);
            padding: 40px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(138, 43, 226, 0.3);
            max-width: 500px;
            width: 90%;
        }
        
        .cross {
            color: #ff3333;
            font-size: 4rem;
            margin-bottom: 20px;
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 20px;
            background: linear-gradient(45deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        p {
            margin-bottom: 30px;
            line-height: 1.6;
        }
        
        .btn {
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 50px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
        }
        
        .btn:hover {
            background: linear-gradient(45deg, var(--secondary), var(--primary));
            box-shadow: 0 0 15px rgba(138, 43, 226, 0.7);
        }
    </style>
</head>
<body>
    <div id="particles-js"></div>
    
    <div class="cancel-container">
        <div class="cross">✕</div>
        <h1>Payment Cancelled</h1>
        <p>Your payment was cancelled. No charges have been made to your account.</p>
        <a href="/" class="btn">Return to Home</a>
    </div>

    <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
    <script>
        // Initialize particles.js
        particlesJS('particles-js', {
            particles: {
                number: { value: 80, density: { enable: true, value_area: 800 } },
                color: { value: "#8a2be2" },
                shape: { type: "circle" },
                opacity: { value: 0.5, random: true },
                size: { value: 3, random: true },
                line_linked: {
                    enable: true,
                    distance: 150,
                    color: "#9370db",
                    opacity: 0.4,
                    width: 1
                },
                move: {
                    enable: true,
                    speed: 2,
                    direction: "none",
                    random: true,
                    straight: false,
                    out_mode: "out",
                    bounce: false
                }
            },
            interactivity: {
                detect_on: "canvas",
                events: {
                    onhover: { enable: true, mode: "repulse" },
                    onclick: { enable: true, mode: "push" },
                    resize: true
                }
            },
            retina_detect: true
        });
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)
