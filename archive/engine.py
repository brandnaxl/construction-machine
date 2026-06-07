import json 
from decimal import Decimal 

with open ('pricing.json', 'r')as f : 
    PRICING_DATA = json.load(f)

def calculate_aluminum(width_cm, height_cm, vendor_base_price, glass_type, brand_name):
    width_m = Decimal(width_cm) / Decimal(100)
    height_m = Decimal(height_cm) / Decimal(100) 
    area_m2 = width_m * height_m
    vendor_price = Decimal(vendor_base_price)

    #1. check brand aluminum (astral ap , ykk , etc)
    if brand_name in PRICING_DATA["aluminum_multipliers"]:
        multiplier_value = PRICING_DATA["aluminum_multipliers"][brand_name]
    else: 
        print(f"WARNING : Brand '{brand_name}' not found.")

    alum_multiplier = Decimal(str(multiplier_value))
    total_alum = vendor_base_price * alum_multiplier

    #2. Kaca 
    if glass_type in PRICING_DATA["glass_prices"]:
        glass_value = PRICING_DATA["glass_prices"][glass_type]
    else : 
        print(f"Warning! '{glass_type}' kagak ada blay")
        
    glass_count = Decimal(str(glass_value))
    total_glass = area_m2 * glass_count

    #3.Tenaga Kerja 
    sealant_value = Decimal(PRICING_DATA["sealant_fees_per_m"]["sealant"])
    total_sealant = sealant_value * area_m2

    grand_total = total_alum + total_glass + total_sealant

    return { 
        "brand_used" : brand_name, 
        "multiplier_used" : float(alum_multiplier),
        "cost_aluminum" : round(total_alum, 0),
        "grand_total" : round(grand_total, 0)
    }


## def analyze_profitability(item_data, discount_percent, architect_fee_percent=0):

    #ini item data apa ya ? coba tanya kok dia bisa kita pake untuk ngamboil nilai dari atas ? 
    """
    Takes the raw item data and applies Discounts, VAT, and Margin logic.
    """
    
    # Load Financials
    ppn_rate = Decimal(str(PRICING_DATA["financials"]["ppn_percent"]))
    
    # 1. Get Totals (Ambil Data dasar)
    gross_sell_total = Decimal(item_data["selling"]["total_price"])
    total_base_cost = Decimal(item_data["costing"]["total_cost"])
    vendor_base_total = Decimal(item_data["costing"]["vendor_base_total"]) # For Input VAT

    # 2. Apply Customer Discount (Jumlah yang dibayar Customer)
    disc_decimal = Decimal(discount_percent) / Decimal(100)
    discount_amount = gross_sell_total * disc_decimal
    price_after_discount = gross_sell_total - discount_amount

    # 3. PPN Analysis 
    ppn_out = (price_after_discount/(1+ppn_rate)) * ppn_rate
    ppn_in = (vendor_base_total/(1+ppn_rate)) * ppn_rate
    ppn_difference = ppn_out - ppn_in

    # 4. Fee Arsitek / Kontraktor 
    arch_decimal = Decimal(architect_fee_percent /Decimal(100))
    architect_fee = price_after_discount * arch_decimal

    #5. Gross Income 
    gross_income = price_after_discount - ppn_difference - total_base_cost - architect_fee

    #6. Margin 
    if gross_income > 0 : 
        margin_percent = ((gross_income / price_after_discount)*100)
    else : 
        margin_percent = 0 

    return {
        "final_invoice_price": round(price_after_discount + ppn_out, 0), # Price + Tax
        "final_price" : round(gross_sell_total),
        "total_base_cost": round(total_base_cost, 0),
        "gross_income": round(gross_income, 0),
        "margin_percent": round(margin_percent, 1),
        "debug": {
            "discount_amount": round(discount_amount, 0),
            "architect_fee": round(architect_fee, 0),
            "ppn_diff": round(ppn_difference, 0),
            "ppn_in" : round(ppn_in,0),
            "ppn_out" : round(ppn_out,0)
        }
    }
