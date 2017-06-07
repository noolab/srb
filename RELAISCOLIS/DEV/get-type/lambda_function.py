def getType(event, context):
    true=True
    false=False
    data={
      "type": "dropoff",
      "postal": false,
      "pickup": false,
      "dropoff": true,
      "linehaul": false
    }
    return data