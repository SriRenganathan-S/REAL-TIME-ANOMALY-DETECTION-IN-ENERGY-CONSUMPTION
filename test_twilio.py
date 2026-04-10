import sys
try:
    from twilio.rest import Client
except ImportError:
    print("Twilio library not found.")
    sys.exit(1)

# The exact credentials you just saved in alert_system.py
ACCOUNT_SID = 'AC62a66ce4e128af99857bfa8e7f07e3eb'
AUTH_TOKEN = '07f410e52a7701cc595bc2739a59bc37'
TWILIO_PHONE = '+18123125108'
MY_PHONE = '+917418921860' 

try:
    print("=====================================")
    print("📞 TWILIO ISOLATION TEST 📞")
    print("=====================================")
    print(f"Attempting to call {MY_PHONE} from {TWILIO_PHONE}...")
    
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    call = client.calls.create(
        twiml='<Response><Say>Hello Sri! This is your Energy System confirming your Twilio configuration works flawlessly.</Say></Response>',
        to=MY_PHONE,
        from_=TWILIO_PHONE
    )
    print(f"\n✅ SUCCESS! Call dispatched to Twilio Cloud.")
    print(f"✅ Call ID: {call.sid}")
    print("\n👉 Your phone should be ringing literally right now! If it isn't, Twilio is delaying the trial call.")
    
except Exception as e:
    print(f"\n❌ TWILIO API HAS REJECTED THE CALL!")
    print(f"❌ EXACT REASON: {e}")
