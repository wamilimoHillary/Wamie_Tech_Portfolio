"""
app/mpesa/mpesa_routes.py
Flask routes for M-Pesa STK Push
"""
from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, session
from app.mpesa.mpesa_utils import stk_push, stk_query

mpesa_bp = Blueprint('mpesa', __name__, url_prefix='/mpesa')


@mpesa_bp.route('/pay', methods=['POST'])
def pay():
    """Initiate STK Push from the coffee/booking form."""
    phone  = request.form.get('mpesa-number', '').strip()
    amount = request.form.get('amount', '').strip()

    if not phone or not amount:
        flash("Phone number and amount are required.", "danger")
        return redirect(url_for('main.index'))

    try:
        amount = int(float(amount))
        if amount < 1:
            raise ValueError("Amount must be at least KES 1")
    except ValueError as e:
        flash(f"Invalid amount: {e}", "danger")
        return redirect(url_for('main.index'))

    try:
        result = stk_push(
            phone=phone,
            amount=amount,
            account_ref="WamieTech",
            description="Buy Me Coffee"
        )

        checkout_id = result.get("CheckoutRequestID")
        response_code = result.get("ResponseCode")

        if response_code == "0":
            flash("✅ STK Push sent! Check your phone and enter your M-Pesa PIN.", "success")
            # Store checkout_id in session so we can query it later
            session['mpesa_checkout_id'] = checkout_id
        else:
            flash(f"M-Pesa error: {result.get('ResponseDescription', 'Unknown error')}", "danger")

    except Exception as e:
        flash(f"Payment failed: {str(e)}", "danger")

    return redirect(url_for('main.index'))


@mpesa_bp.route('/buy-coffee', methods=['POST'])
def buy_coffee():
    """Alias route used by the base.html coffee modal form."""
    return pay()


@mpesa_bp.route('/callback', methods=['POST'])
def callback():
    """Daraja callback — Safaricom POSTs the result here."""
    data = request.get_json(silent=True) or {}
    print("📩 M-Pesa Callback received:", data)

    try:
        stk_callback = data['Body']['stkCallback']
        result_code  = stk_callback.get('ResultCode')
        result_desc  = stk_callback.get('ResultDesc')
        checkout_id  = stk_callback.get('CheckoutRequestID')

        if result_code == 0:
            # Payment successful — extract metadata
            items = stk_callback['CallbackMetadata']['Item']
            meta  = {i['Name']: i.get('Value') for i in items}
            amount       = meta.get('Amount')
            receipt      = meta.get('MpesaReceiptNumber')
            phone        = meta.get('PhoneNumber')
            paid_at      = meta.get('TransactionDate')

            print(f"✅ Payment SUCCESS | Receipt: {receipt} | Amount: {amount} | Phone: {phone} | Time: {paid_at}")
            # TODO: save to DB — insert into payments table here

        else:
            print(f"❌ Payment FAILED | Code: {result_code} | Desc: {result_desc}")

    except (KeyError, TypeError) as e:
        print(f"⚠️ Callback parsing error: {e}")

    # Always return 200 to Safaricom
    return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"}), 200


@mpesa_bp.route('/query', methods=['POST'])
def query():
    """Check the status of a pending STK push (AJAX endpoint)."""
    checkout_id = request.json.get('checkout_id') or session.get('mpesa_checkout_id')

    if not checkout_id:
        return jsonify({"error": "No checkout ID provided"}), 400

    try:
        result = stk_query(checkout_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mpesa_bp.route('/test', methods=['GET'])
def test_page():
    """Simple sandbox test page."""
    return render_template('mpesa/test.html')
