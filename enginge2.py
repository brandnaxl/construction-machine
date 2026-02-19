import json 
from decimal import Decimal 
from decimal import Decimal, ROUND_UP, ROUND_HALF_UP

with open ('pricing.json', 'r')as f : 
    PRICING_DATA = json.load(f)


def ceiling_1000(value):
    """
    niru fungsi =CEILING(value, 1000) di Excel.
    B angka ke atas ke kelipatan 1000 terdekat.
    """
    # Dibagi 1000, dibulatkan ke atas, lalu dikali 1000 lagi
    return (value / Decimal('1000')).quantize(Decimal('1'), rounding=ROUND_UP) * Decimal('1000')

def calculate_aluminum(width_cm, height_cm,quantity, vendor_base_price, glass_type, brand_name):
    width_m = Decimal(width_cm) / Decimal(100)
    height_m = Decimal(height_cm) / Decimal(100) 
    area_m2 = width_m * height_m
    area_m = (Decimal('4')*width_m)+(Decimal('4')*height_m)
    qty = Decimal(quantity)
    vendor_base_unit = Decimal(vendor_base_price)
    ppn_rate = Decimal(str(PRICING_DATA["financials"]["ppn_percent"]))

    #=======================
    # SELLING PRICE 
    #=======================
    #1. check brand aluminum (astral ap , ykk , etc)
    # masukin harga base vendor pake harga satuannya --> (cek) soalnya ada masalah
    if brand_name in PRICING_DATA["aluminum_multipliers"]:
        multiplier_value = PRICING_DATA["aluminum_multipliers"][brand_name]
    else: 
        print(f"WARNING : Brand '{brand_name}' not found.")

    alum_multiplier = Decimal(str(multiplier_value))
    sell_alum_unit= Decimal(vendor_base_price * alum_multiplier) #harga jual alumunium

    #2. Kaca 
    if glass_type in PRICING_DATA["glass_prices"]:
        glass_value = PRICING_DATA["glass_prices"][glass_type]
    else : 
        print(f"Warning! '{glass_type}' kagak ada blay")
        
    glass_count = Decimal(PRICING_DATA["glass_prices"][glass_type]["sell"])
    sell_glass_unit = area_m2 * glass_count

    #3.Sealant
    ## ada masalah ini 
    sealant_value = Decimal(PRICING_DATA["sealant_fees_per_m"]["sealant"])
    total_sealant = sealant_value * area_m

    #Grand total Selling
    unit_selling_price = sell_alum_unit + sell_glass_unit + total_sealant
    total_selling_price = unit_selling_price * qty

    #================
    # BASE PRICE 
    #================

    #1 Material Cost 
    cost_alum_unit = vendor_base_unit
    glass_buy_rate = Decimal(PRICING_DATA["glass_prices"][glass_type]["buy"])
    cost_glass_unit = area_m2 * glass_buy_rate

    #operational cost 
    manpower_rate = Decimal(PRICING_DATA["internal_costs_per_m2"]["manpower_base"])
    sealant_rate = Decimal(PRICING_DATA["internal_costs_per_m2"]["sealant_base"])
    
    cost_manpower_unit = manpower_rate * area_m2
    cost_sealant_unit = (sealant_rate * area_m)/2

    #total
    unit_base_cost = cost_alum_unit+cost_glass_unit+cost_manpower_unit+cost_sealant_unit
    total_base_cost = unit_base_cost*qty

    return { 
        "meta":{
             "brand_used" : brand_name, 
             "quantity" : int(qty),
             "area_m2" : float(round(area_m2, 2)),
             "quantity": quantity,
             "vendor_base_price": vendor_base_price,
             "brand_used": brand_name,    # <--- TAMBAHKAN BARIS INI
             "glass_used": glass_type,
             "width_m": width_m,
             "height_m": height_m,
             "width_cm" : width_cm,
             "height_cm" : height_cm
        },
        "selling": {
            "unit_price" : round(unit_selling_price,0),
            "total_price" : round(total_selling_price),
            "breakdown" : {
                "alum": round(sell_alum_unit*qty, 0),
                "glass": round(sell_glass_unit*qty, 0), 
                "sealant":round(total_sealant*qty,0)
            }
        },
        "costing":{
            "unit_cost" : round(unit_base_cost),
            "total_cost" : round(total_base_cost,0) , #modal asli 
            "vendor_base_total" : round(cost_alum_unit *qty,0),#harga asli total dari vendor (untuk kalkulasi ppn ,
            "kaca_base_cost" : round(cost_glass_unit*qty),
            "sealant_base_cost" : round(cost_sealant_unit*qty),
            "manpower_base_cost" : round(cost_manpower_unit*qty)
        }
    }



def analyze_profitability(project_items_list, discount_percent, architect_fee_percent=0, hitung_ppn = True):
    #Load PPN 
    if hitung_ppn:
        ppn_rate = Decimal(str(PRICING_DATA["financials"]["ppn_percent"]))
    else : 
        ppn_rate = Decimal('0') #Bebas PPN

    #2. Penampung buat total 
    grand_gross_sell = Decimal('0') 
    grand_total_base_cost = Decimal('0')
    grand_vendor_base_total = Decimal('0')

    # 3. Kasih Loop: Cart Sementara & Jumlahin Semuanya 
    for item in project_items_list : 
        grand_gross_sell += ceiling_1000(Decimal(item["selling"]["total_price"]))
        grand_total_base_cost += Decimal(item["costing"]["total_cost"])
        grand_vendor_base_total += Decimal(item["costing"]["vendor_base_total"])


    #4. Kalkulasi Diskon Global 
    disc_decimal = Decimal(discount_percent) / Decimal(100)
    discount_amount = grand_gross_sell * disc_decimal

    # Harga ahkir u/ client (include pajak) 
    price_after_discount = grand_gross_sell - discount_amount 

    #5. Ngitung PPN Inclusive 
    ppn_out = ((price_after_discount / (1+ppn_rate)) * ppn_rate)
    ppn_in = (grand_vendor_base_total/(1+ppn_rate)) * ppn_rate
    ppn_difference = ppn_out - ppn_in

    #6. Ngitung Fee Architect 
    arch_decimal = Decimal(architect_fee_percent) / Decimal(100) 
    architect_fee = price_after_discount * arch_decimal 

    #7. Sisa Keuntungan bersih (gross income) 
    gross_income = price_after_discount - ppn_difference - grand_total_base_cost - architect_fee

    #8. Global Margin 
    if price_after_discount > 0 : 
        margin_percent = (gross_income / price_after_discount) * 100 
    else : 
        margin_percent = Decimal ('0')

    #9. Return Data dengan Pembulatan (Menggunakan Ceiling 1000)
    return {
        "grand_list_price" : ceiling_1000(grand_gross_sell), 
        "final_price" : ceiling_1000(price_after_discount), 
        "total_base_cost" : ceiling_1000(grand_total_base_cost), 
        "gross_income" : ceiling_1000(gross_income), 
        "margin_percent" : margin_percent.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP),
        "debug": {
            "discount_amount": round(discount_amount),
            "architect_fee": round(architect_fee),
            "ppn_diff": ppn_difference,
            "ppn_in": ppn_in,
            "ppn_out": ppn_out
        }
    }
    


