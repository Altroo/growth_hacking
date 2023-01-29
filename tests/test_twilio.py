from twilio.rest import Client


account_sid = "AC048c0294e15a86852f1e1a8526e809c0"
auth_token = "5775a9c6203fa2c51cc961bf6a5f1abd"
client = Client(account_sid, auth_token)

message = client.messages.create(
                              body='Hello there from computer!',
                              from_='whatsapp:+212634868898',
                              to='whatsapp:+212662190660'
                          )
print(message)
