function _3dsecure(stripe_publishable_key, pi_secret) {
    document.addEventListener("DOMContentLoaded", function (event) {
        var stripe = Stripe(stripe_publishable_key);
        stripe.confirmCardPayment(pi_secret).then(function (result) {
            if (result.error) {
                $('3ds_result').text("Error :/");
                $('3ds_result').addClass("text-danger")
            }
            else {
                $('3ds_result').text("Thanks for your payment :)");
                $('3ds_result').addClass("text-success")
            }
        })
    })
}