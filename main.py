from random import paretovariate

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_api
# import generic_helper

app = FastAPI()

@app.post("/")
async def handle_request(request: Request):
    # Retrieve the JSON data from the request
    payload = await request.json()

    # Extract the necessary information from the payload
    # based on the structure of the WebhookRequest from Dialogflow
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']

    intent_dict={
        'order.add:ongoing-order': addOrder,
    # 'order.remove - context: ongoing-order': remove_from_order,
    # 'order.complete - context: ongoing-order': complete_order,
    'track.order:context-ordertracking': trackOrder
    }

    return intent_dict[intent](parameters)

def addOrder(parameter:dict):
    food_items=parameter["food-item"]
    quantity=parameter["number"]

    if len(food_items)!=len(quantity):
        fullfillment_text=f"please specify the quanity for each item !"
    else:
        fullfillment_text=f"Recieved order in backend"

    return JSONResponse(content={
        "fulfillmentText":fullfillment_text
    })

def trackOrder(parameter:dict):
       order_id = int(parameter['number'])
       status=db_api.get_order_status(order_id)
       print(status)
       if status:
           fulfillment_text = f"The order status for order id: {order_id} is : {status}"
       else:
           fulfillment_text = f"No order found with order id: {order_id}"

       return JSONResponse(content={
           "fulfillmentText": fulfillment_text
       })
