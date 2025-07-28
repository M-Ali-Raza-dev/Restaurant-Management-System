# ====================================================================== #
#                   Pak Cuisine Restaurant - POS System                  #
#         Tkinter-based Professional Billing & Ordering Interface        #
# ====================================================================== #

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from restaurant_backend import RestaurantManager
import datetime


# --------------------------- Main Application Class --------------------------- #
class RestaurantApp:
    """GUI Application for Restaurant Management using Tkinter."""

    # --------------------------- Initialization --------------------------- #
    def __init__(self, root):
        self.root = root
        self.root.title("🍴 Pak Cuisine Restaurant - Professional POS System")
        self.root.geometry("1500x900")
        self.root.configure(bg="#2c3e50")

        # Start maximized on Windows
        if self.root.tk.call('tk', 'windowingsystem') == 'win32':
            self.root.state('zoomed')

        # Backend Manager Instance
        self.manager = RestaurantManager()

        # Setup UI
        self.setup_styles()
        self.create_widgets()
        self.update_order_display()

    # --------------------------- Tkinter Styles --------------------------- #
    def setup_styles(self):
        """Configure custom styles for the UI."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Notebook (tabs) styles
        self.style.configure("Custom.TNotebook",
                             background="#2c3e50",
                             borderwidth=0,
                             tabmargins=[2, 5, 2, 0])

        self.style.configure("Custom.TNotebook.Tab",
                             font=("Segoe UI", 12, "bold"),
                             padding=[20, 12],
                             background="#34495e",
                             foreground="white",
                             borderwidth=1,
                             focuscolor="none")

        self.style.map("Custom.TNotebook.Tab",
                       background=[("selected", "#e74c3c"), ("active", "#3498db")],
                       foreground=[("selected", "white"), ("active", "white")])

    # --------------------------- Create Main Layout --------------------------- #
    def create_widgets(self):
        """Build the main application layout."""
        # ---------- Header Section ----------
        header_frame = tk.Frame(self.root, bg="#34495e", height=80)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)

        tk.Label(header_frame,
                 text="🍴 PAK CUISINE RESTAURANT",
                 font=("Segoe UI", 32, "bold"),
                 bg="#34495e", fg="#f39c12").pack(side=tk.LEFT, padx=20, pady=20)

        # Date/Time label
        self.datetime_label = tk.Label(header_frame,
                                       font=("Segoe UI", 14),
                                       bg="#34495e", fg="white")
        self.datetime_label.pack(side=tk.RIGHT, padx=20, pady=20)
        self.update_datetime()

        # ---------- Main Container ----------
        main_container = tk.Frame(self.root, bg="#2c3e50")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Panel → Menu
        self.create_menu_panel(main_container)

        # Right Panel → Order & Bill
        self.create_order_panel(main_container)

    # --------------------------- Menu Panel --------------------------- #
    def create_menu_panel(self, parent):
        """Create the menu panel with categories and items."""
        menu_frame = tk.Frame(parent, bg="#2c3e50")
        menu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Title
        tk.Label(menu_frame,
                 text="📋 MENU CATEGORIES",
                 font=("Segoe UI", 20, "bold"),
                 bg="#2c3e50", fg="#ecf0f1").pack(pady=10)

        # Tabbed categories
        self.notebook = ttk.Notebook(menu_frame, style="Custom.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Store references for quantity fields
        self.entries = {}
        for category, items in self.manager.menu.items():
            self.create_menu_tab(category, items)

    def create_menu_tab(self, category, items):
        """Create a tab for each menu category."""
        tab_frame = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(tab_frame, text=category)

        # Scrollable Canvas
        canvas = tk.Canvas(tab_frame, bg="#ecf0f1", highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ecf0f1")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Category Header
        header_frame = tk.Frame(scrollable_frame, bg="#3498db", pady=15)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        tk.Label(header_frame,
                 text=category,
                 font=("Segoe UI", 18, "bold"),
                 bg="#3498db", fg="white").pack()

        # Add menu items
        for item, price in items.items():
            self.create_menu_item(scrollable_frame, category, item, price)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Scroll with mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def create_menu_item(self, parent, category, item, price):
        """Create individual menu item entry with + and - buttons."""
        item_frame = tk.Frame(parent, bg="white", relief="ridge", bd=2)
        item_frame.pack(fill=tk.X, padx=20, pady=5)

        # Item Info
        info_frame = tk.Frame(item_frame, bg="white")
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=15, pady=10)

        tk.Label(info_frame, text=item,
                 font=("Segoe UI", 14, "bold"),
                 bg="white", fg="#2c3e50").pack(anchor="w")

        tk.Label(info_frame, text=f"Rs. {price}",
                 font=("Segoe UI", 12),
                 bg="white", fg="#e74c3c").pack(anchor="w")

        # Quantity Controls
        qty_frame = tk.Frame(item_frame, bg="white")
        qty_frame.pack(side=tk.RIGHT, padx=15, pady=10)

        qty_var = tk.IntVar(value=0)
        self.entries[(category, item)] = qty_var

        # Decrease button
        tk.Button(qty_frame, text="−", font=("Segoe UI", 12, "bold"),
                  bg="#e74c3c", fg="white", width=3,
                  command=lambda: self.change_quantity(qty_var, -1)).pack(side=tk.LEFT)

        # Quantity Entry
        qty_entry = tk.Entry(qty_frame, textvariable=qty_var,
                             font=("Segoe UI", 12), width=5, justify="center")
        qty_entry.pack(side=tk.LEFT, padx=5)
        qty_entry.bind('<KeyRelease>', lambda e: self.update_order_display())

        # Increase button
        tk.Button(qty_frame, text="+", font=("Segoe UI", 12, "bold"),
                  bg="#27ae60", fg="white", width=3,
                  command=lambda: self.change_quantity(qty_var, 1)).pack(side=tk.LEFT)

    # --------------------------- Order & Billing Panel --------------------------- #
    def create_order_panel(self, parent):
        """Create the right-side order panel with summary and bill."""
        order_frame = tk.Frame(parent, bg="#34495e", width=500)
        order_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        order_frame.pack_propagate(False)

        # Order Header
        tk.Label(order_frame, text="🧾 CURRENT ORDER",
                 font=("Segoe UI", 18, "bold"),
                 bg="#34495e", fg="#f39c12").pack(pady=15)

        # Order Number
        self.order_num_label = tk.Label(order_frame,
                                        text=f"Order #{self.manager.order_number:04d}",
                                        font=("Segoe UI", 12, "bold"),
                                        bg="#34495e", fg="white")
        self.order_num_label.pack(pady=5)

        # Customer Name Input
        customer_frame = tk.Frame(order_frame, bg="#34495e")
        customer_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(customer_frame, text="Customer Name:",
                 font=("Segoe UI", 10), bg="#34495e", fg="white").pack(anchor="w")

        self.customer_var = tk.StringVar()
        tk.Entry(customer_frame, textvariable=self.customer_var,
                 font=("Segoe UI", 11), bg="white").pack(fill=tk.X, pady=2)

        # Order Summary Box
        self.order_summary = tk.Text(order_frame, height=10, width=45,
                                     font=("Courier New", 10),
                                     bg="#ecf0f1", fg="#2c3e50",
                                     relief="ridge", bd=2)
        self.order_summary.pack(padx=20, pady=10)

        # Pricing (Discount + Tip)
        pricing_frame = tk.Frame(order_frame, bg="#34495e")
        pricing_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(pricing_frame, text="Discount (%):",
                 font=("Segoe UI", 10), bg="#34495e", fg="white").grid(row=0, column=0, sticky="w")
        self.discount_var = tk.IntVar(value=0)
        tk.Entry(pricing_frame, textvariable=self.discount_var,
                 font=("Segoe UI", 10), width=8).grid(row=0, column=1, padx=5)

        tk.Label(pricing_frame, text="Tip (Rs.):",
                 font=("Segoe UI", 10), bg="#34495e", fg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.tip_var = tk.IntVar(value=0)
        tk.Entry(pricing_frame, textvariable=self.tip_var,
                 font=("Segoe UI", 10), width=8).grid(row=1, column=1, padx=5, pady=5)

        # Auto-update on changes
        self.discount_var.trace('w', lambda *args: self.update_order_display())
        self.tip_var.trace('w', lambda *args: self.update_order_display())

        # Bill Display Box
        tk.Label(order_frame, text="📄 BILL RECEIPT",
                 font=("Segoe UI", 16, "bold"),
                 bg="#34495e", fg="#f39c12").pack(pady=(20, 10))

        self.bill_text = tk.Text(order_frame, height=18, width=55,
                                 font=("Courier New", 9),
                                 bg="#2c3e50", fg="#ecf0f1",
                                 relief="ridge", bd=3)
        self.bill_text.pack(padx=20, pady=10)

        # Action Buttons
        self.create_action_buttons(order_frame)

    # --------------------------- Action Buttons --------------------------- #
    def create_action_buttons(self, parent):
        """Create action buttons: Generate Bill, Save, Clear, New Order."""
        btn_frame = tk.Frame(parent, bg="#34495e")
        btn_frame.pack(fill=tk.X, padx=20, pady=20)

        buttons = [
            ("🧾 Generate Bill", self.generate_bill, "#3498db", 0, 0),
            ("💾 Save Bill", self.save_bill, "#27ae60", 0, 1),
            ("🗑️ Clear All", self.clear_all, "#e74c3c", 1, 0),
            ("📋 New Order", self.new_order, "#f39c12", 1, 1)
        ]

        for text, command, color, row, col in buttons:
            btn = tk.Button(btn_frame, text=text, command=command,
                            font=("Segoe UI", 11, "bold"),
                            bg=color, fg="white",
                            relief="flat", cursor="hand2",
                            padx=10, pady=8)
            btn.grid(row=row, column=col, sticky="ew", padx=5, pady=5)

        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

    # --------------------------- Utility Methods --------------------------- #
    def change_quantity(self, qty_var, change):
        """Increase or decrease an item's quantity."""
        current = qty_var.get()
        new_qty = max(0, current + change)
        qty_var.set(new_qty)
        self.update_order_display()

    def update_order_display(self):
        """Update the live order summary display."""
        # Reset order before rebuilding
        self.manager.order.clear()
        for (category, item), qty_var in self.entries.items():
            qty = qty_var.get()
            if qty > 0:
                self.manager.add_item(category, item, qty)

        # Update summary text box
        self.order_summary.delete(1.0, tk.END)
        if self.manager.order:
            summary_text = []
            for key, qty in self.manager.order.items():
                category, item = key.split(":", 1)
                price = self.manager.menu[category][item]
                total = price * qty
                clean_item = item.split(" ", 1)[-1] if " " in item else item
                summary_text.append(f"{clean_item:<20} x{qty:<3} Rs.{total}")

            amounts = self.manager.calculate_total(self.tip_var.get(), self.discount_var.get())
            summary_text.append("-" * 40)
            summary_text.append(f"{'Subtotal:':<30} Rs.{amounts['subtotal']:.2f}")
            if self.discount_var.get() > 0:
                summary_text.append(f"{'Discount:':<30} -Rs.{amounts['discount_amount']:.2f}")
            summary_text.append(f"{'Tax (5%):':<30} Rs.{amounts['tax_amount']:.2f}")
            if self.tip_var.get() > 0:
                summary_text.append(f"{'Tip:':<30} Rs.{self.tip_var.get():.2f}")
            summary_text.append("-" * 40)
            summary_text.append(f"{'TOTAL:':<30} Rs.{amounts['total']:.2f}")

            self.order_summary.insert(tk.END, "\n".join(summary_text))
        else:
            self.order_summary.insert(tk.END, "No items selected")

    def update_datetime(self):
        """Update and refresh the live date/time display every second."""
        now = datetime.datetime.now()
        time_str = now.strftime("%Y-%m-%d | %H:%M:%S")
        self.datetime_label.config(text=time_str)
        self.root.after(1000, self.update_datetime)

    # --------------------------- Bill Management --------------------------- #
    def generate_bill(self):
        """Generate and display the formatted bill."""
        if not self.manager.order:
            messagebox.showwarning("No Items", "Please select at least one item before generating bill!")
            return

        bill = self.manager.generate_bill(
            tip=self.tip_var.get(),
            discount=self.discount_var.get(),
            customer_name=self.customer_var.get()
        )

        self.bill_text.delete(1.0, tk.END)
        self.bill_text.insert(tk.END, bill)

        messagebox.showinfo("Success", "Bill generated successfully!")

    def save_bill(self):
        """Save bill to a file and record in order history."""
        bill_content = self.bill_text.get(1.0, tk.END).strip()
        if not bill_content or bill_content == "No items in order":
            messagebox.showerror("Error", "No bill to save! Please generate a bill first.")
            return

        filename = f"bill_{self.manager.order_number:04d}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(bill_content)

            # Save in history
            self.manager.save_order_history(bill_content, self.customer_var.get())
            messagebox.showinfo("Saved", f"Bill saved as {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save bill: {str(e)}")

    def clear_all(self):
        """Reset all inputs and clear current order."""
        for qty_var in self.entries.values():
            qty_var.set(0)
        self.tip_var.set(0)
        self.discount_var.set(0)
        self.customer_var.set("")
        self.bill_text.delete(1.0, tk.END)
        self.update_order_display()

    def new_order(self):
        """Start a new order after clearing the current one."""
        if self.manager.order:
            if not messagebox.askyesno("New Order", "Current order will be cleared. Continue?"):
                return

        self.clear_all()
        self.manager.clear_order()
        self.order_num_label.config(text=f"Order #{self.manager.order_number:04d}")
        messagebox.showinfo("New Order", f"Started new order #{self.manager.order_number:04d}")


# --------------------------- Run Application --------------------------- #
if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantApp(root)
    root.mainloop()
