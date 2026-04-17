def process_order(order, inventory, notifier):
    summary = []
    total = 0
    tmp = []

    for item in order["items"]:
        if item["sku"] in inventory:
            if inventory[item["sku"]]["active"]:
                if inventory[item["sku"]]["count"] >= item["quantity"]:
                    line_total = item["quantity"] * item["price"]
                    total += line_total
                    summary.append({"sku": item["sku"], "total": line_total})
                else:
                    notifier.append(f"backorder:{item['sku']}")
            else:
                notifier.append(f"inactive:{item['sku']}")
        else:
            notifier.append(f"missing:{item['sku']}")

    tax = round(total * 0.08, 2)
    shipping = 12 if total < 100 else 0
    final_total = total + tax + shipping
    tmp.append(final_total)

    return {
        "lines": summary,
        "tax": tax,
        "shipping": shipping,
        "final_total": final_total,
    }


def build_invoice_rows(items):
    rows = []
    for item in items:
        total = item["quantity"] * item["price"]
        rows.append({"sku": item["sku"], "quantity": item["quantity"], "total": total})
    return rows


def build_receipt_rows(items):
    rows = []
    for item in items:
        total = item["quantity"] * item["price"]
        rows.append({"sku": item["sku"], "quantity": item["quantity"], "total": total})
    return rows
