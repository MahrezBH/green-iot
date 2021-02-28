function card(stripe_publishable_key, customer_email) {
    document.addEventListener('DOMContentLoaded', function (event) {
        console.log(1);

        var stripe = Stripe(stripe_publishable_key);
        var elements = stripe.elements();
        var style = {
            base: {
                color: '#32325d',
                fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
                fontSmoothing: 'antialiased',
                fontSize: '16px',
                '::placeholder': {
                    color: '#aab7c4'
                }
            },
            invalid: {
                color: '#fa755a',
                iconColor: '#fa755a'
            }
        };

        var card = elements.create('card', { style: style });
        card.mount("#card-element");
        card.addEventListener('change', function (event) {
            var error_display = document.getElementById('card-errors');
            if (event.error) {
                error_display.textContent = event.error.message;
            }
            else {
                error_display.textContent = '';
            }
        });

        var form = document.getElementById('payment-form');
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            stripe.createToken(card).then(function (result) {
                if (result.error) {
                    var error_display = document.getElementById('card-errors');
                    error_display.textContent = result.error.message;
                }
                else {
                    stripe.createPaymentMethod({
                        type: 'card',
                        card: card,
                        billing_details: {
                            email: customer_email
                        }
                    }).then(function (payment_method_result) {
                        if (payment_method_result.error) {
                            var error_display = document.getElementById('card-errors');
                            error_display.textContent = payment_method_result.error.message;
                        }
                        else {
                            var form = document.getElementById('payment-form');
                            var hidden_data = document.createElement('input');
                            hidden_data.setAttribute('type', 'hidden');
                            hidden_data.setAttribute('name', 'payment_method_id');
                            hidden_data.setAttribute('value', payment_method_result.paymentMethod.id);
                            form.appendChild(hidden_data);
                            form.submit()
                        }
                    })

                }
            })
        })

    })
}