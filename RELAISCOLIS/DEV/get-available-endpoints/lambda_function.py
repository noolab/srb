def getAvailableEndpoints(event, context):
    true = True
    false = False
    data = {
      "/": {
        "get": true
      },
      "/type": {
        "get": true
      },
      "/dropoff_points": {
        "get": true
      },
      "/reserve_dropoff_slots": {
        "get": false
      },
      "/status": {
        "get": true
      },
      "/label": {
        "get": true
      }
    }
    return data