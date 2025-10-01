# Stripe-Payment-Gateway-Django-Integration
This documentation provides a **step-by-step guide** for integrating the **Stripe Payment Gateway** into a Django project using **function-based views**. It covers installation, configuration, checkout flow, webhook handling, and testing.

## About Stripe

Stripe is one of the most popular payment gateways for securely processing online transactions. Integrating it with Django allows you to accept credit/debit card payments in your web application.

## 📖 1. Install Dependencies

```python
pip install stripe
```

## 📖 2. Create a Stripe Developer Account

1. Go to [Stripe Signup Page.](https://dashboard.stripe.com/register)
2. Verify your email after registration.
3. Log in to the Stripe dashboard.

    > Note: Stripe accounts are free, and you can use Test Mode for development without charging real cards.
    > 

## 📖 3. Stripe API Keys Setup

After logging into your Stripe account:

- Go to **Developers → API Keys**.
- Copy **Publishable Key** and **Secret Key**.
    - Also from the Dashboard Home you can copy **Publishable Key** and **Secret Key**.
- Create a `.env` file in your Django project root with the Stripe Key also include **STRIPE_WEBHOOK_SECRET**:

```python
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxx
```

## 📖 3. Django Settings

```python
from decouple import config
import stripe

STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY= config("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET")

stripe.api_key = STRIPE_SECRET_KEY
```

## 📖 4. Order Model

```python
from django.db import models

class OrderModel(models.Model):
    ...
    ...
    stripe_checkout_session_id = models.CharField(max_length=200, blank=True, null=True)
    ...
    ...
```

Used `stripe_checkout_session_id` to store the stripe payment session id.

## 📖 5. Checkout Flow

1. User selects a product/order.
2. We create a **Stripe Checkout Session for Payment**.
3. Stripe redirects user to its hosted payment page.
4. On success → Stripe redirects back to `success` page.
5. On cancel → Stripe redirects back to `cancel` page.

    ```python
    import stripe

    def createPaymentView(request, product_id):
        DOMAIN = "http://127.0.0.1:8000"
        product = get_object_or_404(ProductModel, id=product_id)
        order = OrderModel.objects.create(
            user = request.user,
            product=product,
            amount = product.price
        )

        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                'price_data':{
                    'currency':'usd',
                    'unit_amount': int(product.price * 100),
                    'product_data':{
                        'name': product.name
                    }
                },
                'quantity': 1,
            }],
            mode='payment',
            customer_email = request.user.email,
            success_url = DOMAIN + "/success/",
            cancel_url = DOMAIN + "/cancel/",
        )
        
        order.stripe_checkout_session_id = checkout_session.id
        order.save()
        return redirect(checkout_session.url)
    ```

    ```python
    urlpatterns = [
    path('create-payment/<int:product_id>/', createPaymentView, name='create_payment'),
    ]
    ```

## 📖 6. Success & Cancel Pages

```python
def success(request):
    
    return render(request,'product/payment-success.html')

def cancel(request):
    
    return render(request,'product/payment-cancel.html')
```

```python
urlpatterns = [
    path('success/',success,name='success'),
    path('cancel/',cancel,name='cancel'),
]
```

## 📖 7. Handling Webhooks

Even if a user **closes the browser** after paying, Stripe sends a **webhook event** to confirm payment.

That’s why **webhooks are essential** to mark an order as paid.

```python
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def stripeWebhookView(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        
        print(f'Error verifying webhook signature: {e}')
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print("✅ PaymentIntent succeeded:", session['id'])

        try:
            order = OrderModel.objects.get(
                stripe_checkout_session_id=session['id']
            )
            order.is_paid = True
            order.save()
            product = order.product
            product.stock -= 1
            product.save()
            print('Order marked as paid!')
            return redirect('success')
        except OrderModel.DoesNotExist:
            print("⚠️ Order not found for PaymentIntent:", session['id'])

    return redirect('success')

```

```python
urlpatterns = [
    path('stripe-webhook/', stripeWebhookView, name='stripe_webhook'),
]
```

## 📖 8. Configure Stripe Webhook

Stripe sends **events** (like successful payments) to your app via webhooks.

1. Go to **Developers → Webhooks** in the Stripe Dashboard.
2. Click **+ Add endpoint**.
3. Enter your webhook URL (we’ll use ngrok for local testing, e.g., `https://abcd1234.ngrok.io/stripe-webhook/`).
    - Here `stripe-webhook` is the route of the `stripeWebhookView` that’s we create on the `views.py` file.
4. Select events to listen to. For checkout integration:
    - `checkout.session.completed` (important!)
    - You can also include `payment_intent.succeeded`
5. Click **Add endpoint**.
6. Copy the **Webhook Secret** (`whsec_xxxxx`) → Add it to `.env` file.

    > Tip: Stripe requires HTTPS for webhook URLs. That’s why we use ngrok during local development.
    > 

## 📖 9. Install and Run ngrok

ngrok exposes your local server to the internet.

1. Create account on the ngrok website
2. Download ngrok: https://ngrok.com/download
3. Install `ngrok` 
4. After that run ngrok and configure using authentication token. Without create account you cannot find the token
    
    ```bash
    ngrok config add-authtoken <token>
    ```
    
5. Run your Django server:
    
    ```bash
    python manage.py runserver
    ```
    
6. Open a new terminal and start ngrok on the same port (usually 8000):
    
    ```bash
    ngrok http 8000
    ```
    
7. ngrok will display a **public URL**, e.g.:
    
    ```
    Forwarding    https://abcd1234.ngrok.io -> http://127.0.0.1:8000
    ```
    
8. Use this **ngrok URL** as the webhook URL in Stripe Dashboard:
    
    ```
    https://abcd1234.ngrok.io/stripe-webhook/
    ```
    

## 📖 10. Test Payment with Test Cards

Stripe provides **test card numbers**:

| Card Type | Card Number | Expiry | CVC |
| --- | --- | --- | --- |
| Visa | 4242 4242 4242 4242 | Any future date | Any 3 digits |
| Mastercard | 5555 5555 5555 4444 | Any future date | Any 3 digits |
| AMEX | 3782 822463 10005 | Any future date | Any 4 digits |