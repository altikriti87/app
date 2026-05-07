import customtkinter as ctk
import math

# --- Material Design Theme (Dark Theme) ---
ctk.set_appearance_mode("Dark")  
COLOR_BG = "#121212"          # Material Dark Surface
COLOR_SURFACE = "#1E1E1E"     # Elevation 01 Surface
COLOR_PRIMARY = "#BB86FC"     # Material Primary Purple
COLOR_SECONDARY = "#03DAC6"   # Material Secondary Teal
COLOR_TEXT_MAIN = "#FFFFFF"
COLOR_TEXT_DIM = "#B0B0B0"

class MaterialStockCalculator(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Material Stock Averaging")
        self.geometry("450x640")
        self.configure(fg_color=COLOR_BG)

        # Header Area
        self.header = ctk.CTkLabel(
            self, 
            text="Stock Averaging", 
            # Fixed: Changed weight to "bold"
            font=ctk.CTkFont(family="Roboto", size=26, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        self.header.pack(pady=(30, 20))

        # --- Main Card (Surface) ---
        self.card = ctk.CTkFrame(
            self, 
            fg_color=COLOR_SURFACE, 
            corner_radius=16, 
            border_width=1,
            border_color="#333333"
        )
        self.card.pack(padx=25, pady=5, fill="x")

        # Input Rows
        self.target_price = self.create_material_row(self.card, "Target Average", "3.10")
        self.current_price = self.create_material_row(self.card, "Market Price", "3.0")
        self.old_price = self.create_material_row(self.card, "Current Average", "4.08")
        self.old_qty = self.create_material_row(self.card, "Shares Owned", "1000")

        # --- Calculate Button ---
        self.calc_button = ctk.CTkButton(
            self, 
            text="CALCULATE", 
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            height=48,
            fg_color=COLOR_PRIMARY,
            hover_color="#A370DB",
            text_color="#000000",
            corner_radius=24, 
            command=self.calculate
        )
        self.calc_button.pack(pady=25, padx=25, fill="x")

        # --- Results Box ---
        self.result_box = ctk.CTkTextbox(
            self, 
            fg_color=COLOR_SURFACE, 
            text_color=COLOR_TEXT_MAIN,
            font=ctk.CTkFont(family="Consolas", size=14),
            corner_radius=12,
            border_width=1,
            border_color="#333333"
        )
        self.result_box.pack(pady=(0, 20), padx=25, fill="both", expand=True)
        self.result_box.insert("0.0", " Enter values and tap Calculate")

    def create_material_row(self, parent, label_text, default_val):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(pady=8, padx=15, fill="x")

        lbl = ctk.CTkLabel(
            row, 
            text=label_text, 
            # Fixed: Changed weight to "normal" (Tkinter doesn't support "medium")
            font=ctk.CTkFont(family="Roboto", size=13, weight="normal"),
            text_color=COLOR_TEXT_DIM,
            anchor="w"
        )
        lbl.pack(side="left")

        entry = ctk.CTkEntry(
            row, 
            height=36,
            width=110,
            fg_color="#2C2C2C",
            border_color="#444444",
            border_width=1,
            corner_radius=8,
            font=("Roboto", 13),
            justify="center"
        )
        entry.insert(0, default_val)
        entry.pack(side="right")
        
        return entry

    def calculate(self):
        try:
            q1 = float(self.old_qty.get())
            p1 = float(self.old_price.get())
            pm = float(self.current_price.get())
            pt = float(self.target_price.get())
            
            comm_per_share = pm * 0.006 
            effective_price = pm + comm_per_share

            if pt <= effective_price:
                self.show_res(f"⚠️ TARGET MUST BE > {effective_price:.3f}")
                return

            q2 = math.ceil((q1 * (p1 - pt)) / (pt - effective_price))
            
            total_shares = q1 + q2
            total_investment = (q1 * p1) + (q2 * effective_price)
            final_avg = total_investment / total_shares

            output = (
                f" SUMMARY REPORT\n"
                f"{'─'*30}\n"
                f" Effective Price:    {effective_price:.3f}\n"
                f" Required Shares:    {q2:,}\n"
                f" New Investment:     {q2 * effective_price:,.2f}\n"
                f"{'─'*30}\n"
                f" Total Shares:       {total_shares:,}\n"
                f" Final Avg Price:    {final_avg:.3f}\n"
                f"{'─'*30}"
            )
            self.show_res(output)

        except ValueError:
            self.show_res("❌ ERROR: Check your numbers.")

    def show_res(self, text):
        self.result_box.delete("0.0", "end")
        self.result_box.insert("0.0", text)

if __name__ == "__main__":
    app = MaterialStockCalculator()
    app.mainloop()
