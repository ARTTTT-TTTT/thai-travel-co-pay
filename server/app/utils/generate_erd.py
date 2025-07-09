from graphviz import Digraph

dot = Digraph(comment="Thai Travel Co Pay Clone ERD", format="png")
dot.attr(rankdir="TB", fontsize="12")

# 📦 Nodes (Tables)
dot.node("User", "User\nid, username, email, ...")

# 💾 Save and render
dot.render("../../models_erd", cleanup=True)
print("✅ ER Diagram generated as models_erd.png")
