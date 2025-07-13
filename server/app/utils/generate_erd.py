# * RUN ON GOOGLE COLAB
from graphviz import Digraph

dot = Digraph(comment="Thai Travel Co Pay ERD")
dot.attr(rankdir="TB", overlap="false", fontsize="12")

# 📦 Nodes (Tables)
dot.node("User", "User\nuser_id, email, password_hash, phone_number, ...")
dot.node("Tourist", "Tourist\ntourist_id, user_id, citizen_id, laser_code, ...")
dot.node("Operator", "Operator\noperator_id, user_id, business_name, ...")
dot.node("Province", "Province\nprovince_id, name_th, name_en, region, ...")
dot.node("Booking", "Booking\nbooking_id, tourist_id, hotel_operator_id, ...")
dot.node("ECoupon", "ECoupon\ncoupon_id, booking_id, tourist_id, ...")
dot.node(
    "CouponTransaction",
    "CouponTransaction\ntransaction_id, coupon_id, service_operator_id, ...",
)
dot.node("ProjectConfig", "ProjectConfig\nconfig_key, config_value, ...")

# 🔗 Relationships (Edges)
dot.edge("User", "Tourist", label="1 : 1")
dot.edge("User", "Operator", label="1 : 1")
dot.edge("Province", "Tourist", label="1 : * home_province_id")
dot.edge("Province", "Operator", label="1 : * province_id")
dot.edge("Tourist", "Booking", label="1 : *")
dot.edge("Operator", "Booking", label="1 : * hotel_operator_id")
dot.edge("Booking", "ECoupon", label="1 : *")
dot.edge("Tourist", "ECoupon", label="1 : *")
dot.edge("ECoupon", "CouponTransaction", label="1 : *")
dot.edge("Operator", "CouponTransaction", label="1 : * service_operator_id")

# 💾 Save and render
try:
    dot.format = "png"
    dot.render("models_erd", view=False, cleanup=True)
    print("✅ ER Diagram generated as models_erd.png")
except Exception as e:
    print(
        f"❌ Error generating diagram. Please ensure Graphviz is installed and in your system's PATH. Error: {e}"
    )
