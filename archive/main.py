from Angkasa_pricing.archive.engine import calculate_aluminum 

# main.py inputs
my_width = 90
my_height = 210
my_vendor_price = 10000000
my_glass = "tempered_8mm"
my_brand = "astral_ap"  # <--- NEW INPUT

# Run the function with the new variable
result = calculate_aluminum(my_width, my_height, my_vendor_price, my_glass, my_brand)
print(f"Total price is : '{result}' ")
