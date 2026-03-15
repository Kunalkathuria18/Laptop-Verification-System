import pandas as pd

# --- STEP 1: THE DATABASE ---
data = {
    'brand': ['Apple', 'Samsung', 'Asus'],
    'serial_no': ['MBA13M3A', 'GB4PR760S', 'GU605G16AS'],
    'name': [
        'Apple MacBook Air 13 (M3, 2024)', 
        'Samsung Galaxy Book4 Pro (2024)', 
        'ASUS ROG Zephyrus G16 (2024)'
    ],
    'processor': ['Apple M3', 'Intel Core Ultra 7', 'Intel Core Ultra 9'],
    'ram': ['16GB', '16GB', '32GB'],
    'graphics': ['10-core GPU', 'Intel Arc', 'RTX 4070'],
    'battery': ['18 Hours', '21 Hours', '12 Hours'], # Added
    'warranty': ['1 Year AppleCare', '1 Year Standard', '2 Years Global'], # Added
    'rating': [4.9, 2.4, 3.6],
    'sentiment': ['POSITIVE', 'NEGATIVE', 'MODERATE'],
    'summary': [
        'Silent, fast, and amazing battery.',
        'Overheating issues and software bloat.',
        'Great power, inconsistent build quality.'
    ]
}

df = pd.DataFrame(data)

def run_system():
    while True:
        print("\n" + "="*55)
        print("      LAPTOP VERIFICATION & ANALYSIS (PANDAS)")
        print("="*55)
        print("1. Apple | 2. Samsung | 3. Asus | 4. Exit")
        
        choice = input("\nSelect Brand (1-4): ")
        if choice == '4': break
            
        brand_map = {"1": "Apple", "2": "Samsung", "3": "Asus"}
        
        if choice in brand_map:
            selected_brand = brand_map[choice]
            user_serial = input(f"Enter {selected_brand} Serial: ").strip().upper()
            
            # Filter the table
            result = df[(df['brand'] == selected_brand) & (df['serial_no'] == user_serial)]
            
            if not result.empty:
                row = result.iloc[0] 
                
                print("\n" + "----------------------------------------")
                print(f"STATUS: GENUINE {row['brand'].upper()} FOUND")
                print(f"MODEL:    {row['name']}")
                print("----------------------------------------")
                print(f"PROC:     {row['processor']}")
                print(f"RAM:      {row['ram']}")
                print(f"GPU:      {row['graphics']}")
                print(f"BATTERY:  {row['battery']}")   # Now showing
                print(f"WARRANTY: {row['warranty']}")  # Now showing
                print("----------------------------------------")
                
                while True:
                    print("\n1. View Fundamental Analysis")
                    print("2. Back to Main Menu")
                    sub_choice = input("Choice: ")
                    
                    if sub_choice == '1':
                        print("\n" + "!"*45)
                        print(f"ANALYSIS FOR: {row['name']}")
                        print(f"RATING: {row['rating']}/5.0 | {row['sentiment']}")
                        print(f"EXPERT VIEW: {row['summary']}")
                        print("!"*45)
                    elif sub_choice == '2':
                        break
            else:
                print("\n" + "!"*40)
                print("RESULT: No product found / Not Genuine")
                print("!"*40)
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    run_system()
