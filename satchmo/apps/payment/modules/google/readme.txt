To enable the Google checkout module, at the google checkout dashboard put in your the notification url, which by default is https://www.example.com/checkout/google/notification/

Google checkout calls back this url with notifications on the order and payment status.

After a user submits their cart it calls back the notification url with new order received message.

Then after payment google calls back with a payment charged and a seperate payment amount method. This will update the order status and mark how much was paid in satchmo.

Then to post off the item, from the google checkout console mark it as shipped and another call back into the notification url will change the status in satchmo to delivered.