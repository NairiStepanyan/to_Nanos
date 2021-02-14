#!/usr/bin/python

#
# Update Stripe’s internal records of Nanos customers by:
# 1. Inserting the VAT numbers (if any) from Nanos internal tables into the
#    Customer object inside Stripe.
#    Notes:
#        a. Stripe stores this as “tax_ids”.
#        b. We are only concerned with Swiss VAT now.
# 2. Setting the “tax_exempt” status in the Stripe Customer object to “none”
#    for all Swiss customers and “exempt” for all non-Swiss customers.
#

# To handle JSON-encoded Stripe responses (objects)
import json

# Assuming Nanos database table management API's are implemented in 'nanosDB' library
import nanosDB
import stripe
stripe.api_key = "sk_test_unique_number_provided_to_Nanos_by_Stripe"

#
# Usage of main() routine is formal and any other function can encapsulate its body
#

def main():
# Begin main()

    # Retrieve the list of all Nanos ad campaigns
    allCampaignIDs = list_all_campaigns()

    # Fetch campaign details for all retrieved Nanos ad campaigns
    for aCampaignID in allCampaignIDs:
        compaignInfo = get_campaign_details(aCampaignID,)

        # Get client related details using client IDs
        clientInfo = get_client_details(compaignInfo['client_id'],)

        # Based on the gathered client details, request the Stripe Customer object...
        stripeCustomerID = clientInfo['stripe_customer_id']
        objCustomer = stripe.Customer.retrieve(stripeCustomerID, expand=['tax_ids.data.type'],)

        # Decode the returned JSON object to a dictionary
        response = json.loads(objCustomer)

        # Make sure the customer isn't deleted already.  If it is, proceed to the next one.
        if response['deleted']:
            continue

        if 'Swiss' == clientInfo['country']:
            # Do the necessary updates
            stripe.Customer.modify(stripeCustomerID, tax_exempt="none",)
            # Validate the VAT number and update it
            if clientInfo['vat_number']:
                stripe.Customer.modify(stripeCustomerID, tax_ids={"data.type": clientInfo['vat_number']},)

        else:
            stripe.Customer.modify(clientInfo['stripe_customer_id'], tax_exempt="exempt",)

# End main()

if __name__ == "__main__": main()
