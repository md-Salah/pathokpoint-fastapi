from fpdf import FPDF
from io import BytesIO

# Dummy order data
dummy_order = {
    'id': 1,
    'customer_name': 'John Doe',
    'customer_email': 'johndoe@example.com',
    'total': 123.45
}

# Dummy order items
dummy_order_items = [
    {'product_name': 'Book A', 'quantity': 2, 'unit_price': 15.00},
    {'product_name': 'Book B', 'quantity': 1, 'unit_price': 25.00},
    {'product_name': 'Book C', 'quantity': 3, 'unit_price': 10.00}
]


def generate_invoice_pdf(order, order_items):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_title(f"Invoice_{order['id']}")
    
    # Title
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 10, f"Invoice for Order #{order['id']}", ln=True, align='C')
    
    # Customer details
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Customer: {order['customer_name']}", ln=True)
    pdf.cell(0, 10, f"Email: {order['customer_email']}", ln=True)
    
    # Order details header
    pdf.set_font("Arial", 'B', 14)
    pdf.ln(10)
    pdf.cell(0, 10, "Order Items", ln=True)
    
    # Order items
    pdf.set_font("Arial", '', 12)
    for item in order_items:
        pdf.cell(0, 10, f"{item['quantity']} x {item['product_name']} @ ${item['unit_price']:.2f}", ln=True)
    
    # Total
    pdf.set_font("Arial", 'B', 14)
    pdf.ln(10)
    pdf.cell(0, 10, f"Total: ${order['total']:.2f}", ln=True)
    
    # buffer = BytesIO()
    pdf.output('dummy/invoice.pdf')
    # buffer.seek(0)
    # return buffer

# Generate the PDF
generate_invoice_pdf(dummy_order, dummy_order_items)
