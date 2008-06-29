How to set up the FedEx module:

(Note: Each product MUST have a weight of at least .1 pounds for Fedex to give a valid response. If you have a configurable product you will need to set weights on each product option. Otherwise you will get errors when the FedEx module tries to calculate the weight to send to FedEx for the quote.)

Restart or 'bounce' the store by restarting apache or the site if using Lightpd.

Once you've got the module installed its time to get your account set up with FedEx. (It does not work without the following steps)

Go to http://www.fedex.com/us/developer/ 
Log in (you may need to create an account) and go to technical resources. https://www.fedex.com/wpor/web/jsp/drclinks.jsp?links=index.html
Click "Get Started with FedEx Web Services Technical Resources now"
Click "Move to Production"
At the bottom click "Get Production Key"
Answer the questions / Fill out the forms. Note: You will need a FedEx account number.
Save your authentication key and meter number.
Add your meter number to the shop settings after enabling the FedEx shipping module.
Check the box to connect to the production server.

