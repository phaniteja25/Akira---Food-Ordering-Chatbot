from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

app = FastAPI()


in_progress_order = {}

@app.post("/")
async def handle_request(request:Request):

    
    payload = await request.json()

    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']


    session_id = generic_helper.extract_session_id(output_contexts[0]["name"])

    intent_handler_dict = {
        "order_add - context:ongoing-order" : add_order,
        "order_remove - context:ongoing-order": remove_order,
        "order.complete - context: ongoing-order":complete_order,
        "track.order - context: ongoing-tracking":track_order,
        "order.update - context: ongoing-order":update_order
    }

    return intent_handler_dict[intent](parameters,session_id)


def update_order(parameters:dict,session_id):
    food_items = parameters["food_item"]
    quantities  = parameters["number"]

    new_food_dict = dict(zip(food_items,quantities)) 
    curr_food_dict = in_progress_order[session_id]

    if session_id not in in_progress_order:
        fulfillment_text = "Oops!! You do have not created an order. Please create one first"
    else:
        for item, quantity in new_food_dict.items():
            if item not in curr_food_dict:
                fulfillment_text = f"You do not have {item} in your current on going order"
            else:
                curr_food_dict[item] = quantity

        in_progress_order[session_id] = curr_food_dict
        order_str = generic_helper.get_str_from_food_dict(in_progress_order[session_id])
        fulfillment_text = f"Great. Your order has been updated" \
                            f"Here is your current order list {order_str}"\
                            f"Would you like to add/update/remove anything else?"
        
        return JSONResponse(content={
            "fulfillmentText": fulfillment_text
        })
        






        

    #{pizza:2,biryani:1} , #{pizza:2}




def remove_order(parameters:dict,session_id:str):

    remove_items = parameters["food_item"]
    curr_order_dict = in_progress_order[session_id]

    removed_items = []
    no_such_items = []

    for item in remove_items:
        if item not in curr_order_dict:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del curr_order_dict[item]

    if len(removed_items) >0:
        fulfillment_text = f"Removed {",".join(removed_items)} from your order list"

    if len(no_such_items) > 0:
           fulfillment_text = f"Your current order doesnt have {",".join(no_such_items)}"

    if(curr_order_dict.keys()==0):
        fulfillment_text = "Your current order list is empty"
    else:
        order_str = generic_helper.get_str_from_food_dict(curr_order_dict)
        fulfillment_text = f" Here is what is left in your order : {order_str}"

    return JSONResponse(content={
            "fulfillmentText": fulfillment_text
        })










def add_order(parameters:dict,session_id:str):
    food_items = parameters["food_item"]
    quantities  = parameters["number"]

    if len(food_items) != len(quantities):
        fulfillment_text = "Please specify the qunatities properly"
    else:
        new_food_dict = dict(zip(food_items,quantities))

        if session_id not in in_progress_order:
            in_progress_order[session_id] = new_food_dict
        else:
            current_food_dict = in_progress_order[session_id]
            current_food_dict.update(new_food_dict)
            in_progress_order[session_id] = current_food_dict
        
        order_str = generic_helper.get_str_from_food_dict(in_progress_order[session_id])

        fulfillment_text = f"So far you have {order_str}. Do you need anything else"

    return JSONResponse(content={
            "fulfillmentText": fulfillment_text
        })


def complete_order(parametrs:dict,session_id:str):

    if session_id not in in_progress_order:
        fulfillment_text = "Oops!! Something went wrong"
    else:
        order = in_progress_order[session_id]
        order_id  = save_to_db(order)

        if order_id==-1:
         fulfillment_text = "Sorry! I could not process you order in the backend due to some error. Please try again"
        else:
         order_total = db_helper.get_total_price(order_id)
         fulfillment_text = f"Great. We have placed you order." \
                            f"Here is your order id # {order_id}. "\
                            f"Your order total is {order_total} which you can pay at the time of the delivery!"
    
    #removing the placed order form inprogress order
    del in_progress_order[session_id]
    return JSONResponse(content={
            "fulfillmentText": fulfillment_text
        })           
    


def save_to_db(order:dict):
    next_order_id = db_helper.get_next_order_id()

    for food_item,quantity in order.items():
       rcode =  db_helper.insert_food_item(
            food_item,
            quantity,
            next_order_id
        )
       
       if rcode ==-1:
           return -1
    
    db_helper.insert_order_tracking(next_order_id,"in progress")
    return next_order_id




def track_order(parametrs:dict,sessionId:str):
    order_id  = int(parametrs["number"])

    order_status = db_helper.get_order_status(order_id)

    if order_status:
        fulfillment_text = f"The order status for order id: {order_id} is: {order_status}"
    else:
        fulfillment_text = f"Couldnt find the status with order id: {order_id}"
    


    return JSONResponse(content={
            "fulfillmentText": fulfillment_text
        })






    