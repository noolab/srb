
def lambda_handler(event, context):
    true=True
    data={
      "/": {
        "get": true
      },
      "type": {
        "get": true
      },
      "pickup/slots": {
        "get": true
      },
      "price": {
        "get": true
      },
      "status": {
        "get": true
      }
    }
    return data
