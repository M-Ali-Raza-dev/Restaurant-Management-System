# ====================================================================== #
#                       Restaurant Management Backend                   #
#              Handles Menu, Orders, Billing & Order History             #
# ====================================================================== #

import datetime
import json
import os


# --------------------------- Restaurant Manager Class --------------------------- #
class RestaurantManager:
    """Class to manage restaurant menu, customer orders, billing, and order history."""

    # --------------------------- Initialization --------------------------- #
    def __init__(self):
        # Full Restaurant Menu with Categories
        self.menu = {
            "🥗 Starters": {
                "🥟 Chicken Samosa": 80,
                "🥟 Vegetable Samosa": 60,
                "🍗 Seekh Kebab": 180,
                "🍗 Chicken Tikka": 220,
                "🍵 Mixed Pakora": 100,
                "🧅 Onion Bhaji": 90,
                "🌶️ Chili Chicken": 250
            },
            "🍛 Main Course": {
                "🍛 Chicken Biryani": 320,
                "🥘 Beef Biryani": 380,
                "🍛 Mutton Biryani": 450,
                "🍛 Vegetable Biryani": 280,
                "🍲 Chicken Karahi": 650,
                "🍲 Beef Karahi": 750,
                "🍲 Mutton Karahi": 850,
                "🍲 Haleem": 250,
                "🍲 Nihari": 400,
                "🍗 Butter Chicken": 550,
                "🥘 Dal Makhani": 300
            },
            "🥖 Breads & Sides": {
                "🥖 Butter Naan": 50,
                "🥖 Garlic Naan": 60,
                "🥞 Plain Paratha": 40,
                "🥞 Aloo Paratha": 80,
                "🍚 Plain Rice": 60,
                "🥗 Fresh Salad": 90,
                "🥣 Raita": 50,
                "🧅 Pickled Onions": 30
            },
            "🥤 Beverages": {
                "🥤 Coca Cola": 80,
                "🥤 Sprite": 80,
                "💧 Mineral Water": 50,
                "☕ Kashmiri Chai": 70,
                "☕ Green Tea": 60,
                "🥛 Sweet Lassi": 120,
                "🥛 Mango Lassi": 140,
                "🧃 Fresh Juice": 100
            },
            "🍮 Desserts": {
                "🍮 Rice Kheer": 140,
                "🍩 Gulab Jamun": 120,
                "🍦 Kulfi": 180,
                "🍯 Jalebi": 150,
                "🥧 Ras Malai": 160,
                "🍰 Gajar Halwa": 130
            }
        }

        # Holds the current order
        self.order = {}

        # Assign next order number
        self.order_number = self.get_next_order_number()

    # --------------------------- Order Number Handling --------------------------- #
    def get_next_order_number(self):
        """Generate and save the next sequential order number."""
        try:
            with open("order_counter.json", "r") as f:
                data = json.load(f)
                order_num = data.get("last_order", 0) + 1
        except FileNotFoundError:
            order_num = 1

        with open("order_counter.json", "w") as f:
            json.dump({"last_order": order_num}, f)

        return order_num

    # --------------------------- Order Item Management --------------------------- #
    def add_item(self, category, item, quantity):
        """Add an item with a specific quantity to the current order."""
        if category in self.menu and item in self.menu[category]:
            key = f"{category}:{item}"
            if quantity > 0:
                self.order[key] = self.order.get(key, 0) + quantity
            elif key in self.order:
                del self.order[key]

    def remove_item(self, category, item):
        """Remove an item completely from the current order."""
        key = f"{category}:{item}"
        if key in self.order:
            del self.order[key]

    def clear_order(self):
        """Clear all items from the current order and reset order number."""
        self.order.clear()
        self.order_number = self.get_next_order_number()

    # --------------------------- Billing & Calculation --------------------------- #
    def calculate_total(self, tip=0, discount=0):
        """Calculate subtotal, discount, tax, tip, and final total."""
        subtotal = 0

        # Calculate subtotal
        for key, qty in self.order.items():
            category, item = key.split(":", 1)
            price = self.menu[category][item]
            subtotal += price * qty

        # Apply discount
        discount_amount = (subtotal * discount) / 100
        discounted_subtotal = subtotal - discount_amount

        # Add 5% tax
        tax_amount = (discounted_subtotal * 5) / 100

        # Final total including tip
        total = discounted_subtotal + tax_amount + tip

        return {
            'subtotal': subtotal,
            'discount_amount': discount_amount,
            'discounted_subtotal': discounted_subtotal,
            'tax_amount': tax_amount,
            'tip': tip,
            'total': total
        }

    def generate_bill(self, tip=0, discount=0, customer_name=""):
        """Generate a formatted customer bill."""
        if not self.order:
            return "No items in order"

        amounts = self.calculate_total(tip, discount)
        bill = []

        # --------------------------- Bill Header --------------------------- #
        bill.append("═" * 50)
        bill.append("        🌟 PAK CUISINE RESTAURANT 🌟")
        bill.append("          Premium Pakistani Cuisine")
        bill.append("═" * 50)
        bill.append(f"Order #: {self.order_number:04d}")
        bill.append(f"Date: {datetime.datetime.now().strftime('%d/%m/%Y')}")
        bill.append(f"Time: {datetime.datetime.now().strftime('%H:%M:%S')}")
        if customer_name:
            bill.append(f"Customer: {customer_name}")
        bill.append("─" * 50)
        bill.append(f"{'ITEM':<25} {'QTY':<5} {'PRICE':<8} {'TOTAL':<10}")
        bill.append("─" * 50)

        # --------------------------- Bill Items --------------------------- #
        for key, qty in sorted(self.order.items()):
            category, item = key.split(":", 1)
            unit_price = self.menu[category][item]
            total_price = unit_price * qty

            # Remove emojis for display
            clean_item = item.encode("ascii", "ignore").decode()
            bill.append(f"{clean_item:<25} {qty:<5} Rs.{unit_price:<6} Rs.{total_price:<8}")

        # --------------------------- Bill Footer --------------------------- #
        bill.append("─" * 50)
        bill.append(f"{'Subtotal:':<35} Rs.{amounts['subtotal']:.2f}")
        if discount > 0:
            bill.append(f"{'Discount (' + str(discount) + '%):':<35} -Rs.{amounts['discount_amount']:.2f}")
            bill.append(f"{'After Discount:':<35} Rs.{amounts['discounted_subtotal']:.2f}")
        bill.append(f"{'Tax (5%):':<35} Rs.{amounts['tax_amount']:.2f}")
        if tip > 0:
            bill.append(f"{'Tip:':<35} Rs.{tip:.2f}")
        bill.append("─" * 50)
        bill.append(f"{'TOTAL:':<35} Rs.{amounts['total']:.2f}")
        bill.append("═" * 50)
        bill.append("        🍴 Thank You for Dining With Us! 🍴")
        bill.append("           Please Visit Again Soon ❤️")
        bill.append("═" * 50)
        bill.append("")
        bill.append("Contact: +92-21-1234567 | www.pakcuisine.pk")

        return "\n".join(bill)

    # --------------------------- Order Summary & History --------------------------- #
    def get_order_summary(self):
        """Return a short summary of the current order."""
        if not self.order:
            return "No items selected"

        summary = []
        total_items = 0
        for key, qty in self.order.items():
            category, item = key.split(":", 1)
            clean_item = item.split(" ", 1)[-1] if " " in item else item
            summary.append(f"{clean_item} x{qty}")
            total_items += qty

        return f"{total_items} items: " + ", ".join(summary)

    def save_order_history(self, bill_content, customer_name=""):
        """Save the order details permanently in order_history.json."""
        history_entry = {
            "order_number": self.order_number,
            "date": datetime.datetime.now().isoformat(),
            "customer_name": customer_name,
            "items": dict(self.order),
            "bill": bill_content
        }

        # Load existing history if available
        try:
            with open("order_history.json", "r") as f:
                history = json.load(f)
        except FileNotFoundError:
            history = []

        # Append new order and save
        history.append(history_entry)
        with open("order_history.json", "w") as f:
            json.dump(history, f, indent=2)
