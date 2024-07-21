import re
def extract_session_id(session_str:str):
    match = re.search(r"/sessions/(.*?)/contexts/",session_str)

    if match:
        extracted_string = match[1]
        return extracted_string



def get_str_from_food_dict(food_dict:dict):
    return ", ".join([f"{int(value)} {key}" for key,value in food_dict.items()]) 

if __name__=="__main__":
    # print(extract_session_id("projects/akira-chat-bot-429621/agent/sessions/79426f93-d346-0884-c5fe-ba3524f60a2f/contexts/ongoing-order"))
    print(get_str_from_food_dict({"Pizza":2,"biryani":3}))