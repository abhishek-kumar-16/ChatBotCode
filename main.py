from random import paretovariate

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_api
import methods

app = FastAPI()
inprogress_orders = {}
@app.post("/")
async def handle_request(request: Request):
    # Retrieve the JSON data from the request
    payload = await request.json()

    # Extract the necessary information from the payload
    # based on the structure of the WebhookRequest from Dialogflow
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']
    session_id=methods.extract_session_id(output_contexts[0]["name"])
    intent_dict={
        'order.add:ongoing-order': addOrder,
    # 'order.remove - context: ongoing-order': remove_from_order,
    # 'order.complete - context: ongoing-order': complete_order,
    'track.order:context-ordertracking': trackOrder
    }

    return intent_dict[intent](parameters,session_id)

def addOrder(parameter:dict,sessionId:str):
    food_items=parameter["food-item"]
    quantity=parameter["number"]

    if len(food_items)!=len(quantity):
        fulfillment_text=f"please specify the quanity for each item !"
    else:
        new_order_dict=dict(zip(food_items, quantity))
        if sessionId in inprogress_orders:
            current_food_order=inprogress_orders[sessionId]
            current_food_order.update(new_order_dict)
            inprogress_orders[sessionId]=current_food_order
        else:
            inprogress_orders[sessionId]=new_order_dict

        order_str = methods.get_str_from_food_dict(inprogress_orders[sessionId])
        fulfillment_text = f"So far you have: {order_str}. Do you need anything else?"

    return JSONResponse(content={
        "fulfillmentText":fulfillment_text
    })

def complete_order(parameters:dict,session_id:str):
    


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


