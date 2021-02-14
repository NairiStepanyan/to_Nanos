#!/usr/bin/python

#
# Use Nanos and Stripe APIs along with the provided 'render_tax_invoice()'
# function to create a tax-invoice for a given ad campaign.
#    Note: the 'ad_campaign_id' is an input to the method to be created
#

# To handle JSON-encoded Stripe responses (objects)
import json

# Assuming Nanos database table management API's are implemented in 'nanosDB' library
import nanosDB
import stripe
stripe.api_key = "sk_test_unique_number_provided_to_Nanos_by_Stripe"

#
# A helper function.
# Input: Dictionary holding address info
# Output: String containing pure address
#
def constructAddress(aAddress):
# Begin constructAddress()

    # Not using inbuilt dictionary routines here, to
    # get a specific/proper order of address details
    result = ""

    if aAddress['line1']:
        result = aAddress['line1'] + ", "
    if aAddress['line2']:
        result += aAddress['line2'] + ", "
    if aAddress['city']:
        result += aAddress['city'] + ", "
    if aAddress['state']:
        result += aAddress['state'] + ", "
    if aAddress['postal_code']:
        result += aAddress['postal_code'] + ", "
    if aAddress['country']:
        result += aAddress['country']

    return result

# End constructAddress()

#
# A method to create a tax-invoice for a specific ad campaign
# Input: Campaign ID
# Output: None
#
def create_tax_invoice(ad_campaign_id):
# Begin create_tax_invoice()

    client_name = "n/a"
    email = "n/a"
    address = "n/a"
    campaign_name = "n/a"
    invoice_currency = "n/a"
    invoice_amount = 0
    vat_amount = 0
    net_amount = 0

    # Get the details of the given Nanos ad campaign
    campaignInfo = get_campaign_details(ad_campaign_id)
    campaign_name = campaignInfo['name']

    # Acquire the Charge object associated with current ad campaign
    objCharge = stripe.Charge.retrieve(campaignInfo['stripe_charge_id'],)

    # Decode the gathered JSON response
    response = json.loads(objCharge)

    # Retrieve/calculate the required client info
    if response['billing_details']['name']:
        client_name = response['billing_details']['name']
    if response['billing_details']['email']:
        email = response['billing_details']['email']

    address = constructAddress(response['billing_details']['address'])
    invoice_currency = response['currency']

    if response['amount']:
        invoice_amount = response['amount']
        vat_amount = invoice_amount * 7.7 / 100
        net_amount = invoice_amount - vat_amount

    # Call the provided method to create a tax-invoice
    render_tax_invoice(client_name, email, address, campaign_name, invoice_currency,
                       invoice_amount, vat_amount, net_amount)

# End create_tax_invoice()
