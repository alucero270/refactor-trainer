def export_customer_rows(customers):
    rows = []
    normalized = [customer.strip() for customer in customers]
    cleaned = [customer for customer in normalized if customer]
    lowered = [customer.lower() for customer in cleaned]
    unique = sorted(set(lowered))
    pairs = [(index + 1, customer) for index, customer in enumerate(unique)]
    rows.extend({"id": index, "name": customer} for index, customer in pairs)
    return rows
