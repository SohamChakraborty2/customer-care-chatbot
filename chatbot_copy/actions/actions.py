
from typing import Any, Text, Dict, List
from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.executor import CollectingDispatcher
import requests
from rasa_sdk.events import SlotSet , FollowupAction , AllSlotsReset , Restarted
import re

ticketCount=0
OFFER1 ={"plan1", "plan 1","Plan 1","Plan1"}
OFFER2 ={"plan2","plan 2","Plan 2","Plan2"}
OFFER3 ={"plan3","plan 3","Plan 3","Plan3"}

# starting SIM form
class ValidateSimTypeForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_sim_type_form"

    def validate_sim_type(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[str, str],
    ) -> Dict[str, str]:
        sim_name = tracker.get_slot("sim_type")

        if not sim_name:
            dispatcher.utter_message(text="This field can't be empty.")
            return {"sim_type": None}
        elif sim_name.lower() == "e-sim" or sim_name.lower() == "physical":
            return {"sim_type": sim_name}
        else:
            dispatcher.utter_message(text="Invalid value")
            return{"sim_type": None}
        
    def validate_zipcode(
        self,
        slot_value:Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate 'account_number' value."""
        num = tracker.get_slot("zipcode")
    

        if not num.isdigit() or len(num) != 6:
            dispatcher.utter_message(text="Invalid zipcode.")
            return {"zipcode": None}
        else:
            return {"zipcode": num}
        
# getting SIM price
class ActionSIMPrice(Action):
    def name(self) -> Text:
        return "action_sim_price"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
       domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        sim_type = tracker.get_slot("sim_type")
        sim_type= sim_type.lower()
        try:
                api_url =f"http://127.0.0.1:5000/api/user/get?sim_type={sim_type}&channel=web&input=SIM_TYPE"
                response = requests.get(api_url)
                user_data = response.json()
                response_code = user_data.get("responseCode", 500)  
                response_desc = user_data.get("responseDesc", "Unknown error")

                if response_code == 200 and response_desc == "Success":
                    sim_price = user_data.get("Price")
                    return[SlotSet("sim_price",sim_price), FollowupAction("confirm_sim_selection_form")]
                    
        except Exception as e:
                dispatcher.utter_message(text="An error occurred while processing. Please try again later.") 
                dispatcher.utter_message(template="utter_menu2")
                return [SlotSet("latest_intent", "greet"),SlotSet("sim_type",None),SlotSet("zipcode",None)]
                

# confirming the details of sim type n zipcode along with price                
class ValidateSimSelectionForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_confirm_sim_selection_form"
    def validate_confirm_sim_type(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[str, str],
    ) -> Dict[str, str]:
        intent = tracker.get_intent_of_latest_message()
        decision = tracker.get_slot("confirm_sim_type")

        if not decision:
            dispatcher.utter_message(text="Invalid input.")
            return {"confirm_sim_type": None}
        if decision is not None:
            if intent in ["affirm", "deny"]:
                return {"confirm_sim_type": intent}
            else:
                dispatcher.utter_message(text="Invalid input.")
                return {"confirm_sim_type": None}

# showcasing the plans
class ActionSimTypeForm(Action):
    def name(self) -> Text:
        return "action_submit_sim_type_form"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
       domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        sim_type = tracker.get_slot("sim_type")
        sim_type=sim_type.lower()
        confirmation = tracker.get_slot("confirm_sim_type")
        if confirmation=="affirm":
            try:
                api_url =f"http://127.0.0.1:5000/api/user/get?sim_type={sim_type}&channel=web&input=SIM_TYPE"
                response = requests.get(api_url)
                user_data = response.json()
                response_code = user_data.get("responseCode", 500)  
                response_desc = user_data.get("responseDesc", "Unknown error")

                if response_code == 200 and response_desc == "Success":
                    offer1 = user_data.get("Offer 1")
                    price1= user_data.get("Price 1")
                    price2= user_data.get("Price 2")
                    price3= user_data.get("Price 3")
                    offer2 = user_data.get("Offer 2")
                    offer3 = user_data.get("Offer 3")
                    message = f"Plan 1: {offer1}, ${price1}\nPlan 2: {offer2}, ${price2}\nPlan 3: {offer3}, ${price3}"
                    dispatcher.utter_message(text=message)
                    return[FollowupAction("plan_form")]
                else:
                    dispatcher.utter_message(text=f"Error: {response_desc}")
                    dispatcher.utter_message(template="utter_menu2")
                    return [SlotSet("latest_intent", "greet")] + [SlotSet(slot, None) for slot in tracker.slots if slot != "latest_intent"]
            except Exception as e:
                dispatcher.utter_message(text="An error occurred while processing. Please try again later.")
                dispatcher.utter_message(template="utter_menu")
                return [SlotSet("latest_intent", "greet")] + [SlotSet(slot, None) for slot in tracker.slots if slot != "latest_intent"]
        else:
            dispatcher.utter_message(text="Order Cancelled")
            dispatcher.utter_message(template="utter_menu2")
            return [AllSlotsReset(),Restarted()]


# giving option to choose plan
class ValidatePlanForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_plan_form"

    def validate_offer(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[str, str],
    ) -> Dict[str, str]:
        offer= tracker.get_slot("offer")
        
        if offer in OFFER1 or offer in OFFER2 or offer in OFFER3:
            return {"offer": offer}
        else:
            dispatcher.utter_message(text="Invalid Plan")
            return {"offer":None}

# totalling the bill
class ActionSetPrice(Action):
    def name(self) -> Text:
        return "action_set_price"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
       domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        offer = tracker.get_slot("offer")
        sim_type = tracker.get_slot("sim_type")
        sim_type=sim_type.lower()
        if offer!=None:
            try:
                api_url =f"http://127.0.0.1:5000/api/user/get?sim_type={sim_type}&channel=web&input=SIM_TYPE"
                response = requests.get(api_url)
                user_data = response.json()
                response_code = user_data.get("responseCode", 500)  
                response_desc = user_data.get("responseDesc", "Unknown error")

                if response_code == 200 and response_desc == "Success":
                    sim_price = user_data.get("Price")
                    if offer in OFFER1:
                        detail = user_data.get("Offer 1")
                        price1= user_data.get("Price 1")
                        plan_price = int(price1)
                        total = int(price1)+int(sim_price)
                        tax = total/10
                        bill= tax+total
                        return[SlotSet("tax",tax),SlotSet("plan_price",plan_price),SlotSet("total_price",bill),SlotSet("plan_detail",detail),FollowupAction("confirm_plan_selection_form")]
                    elif offer in OFFER2:
                        detail = user_data.get("Offer 2")
                        price2= user_data.get("Price 2")
                        plan_price = int(price2)
                        total = int(price2)+int(sim_price)
                        tax = total/10
                        bill= tax+total
                        return[SlotSet("tax",tax),SlotSet("plan_price",plan_price),SlotSet("total_price",bill),SlotSet("plan_detail",detail),FollowupAction("confirm_plan_selection_form")]
                    elif offer in OFFER3:
                        detail = user_data.get("Offer 3")
                        price3= user_data.get("Price 3")
                        plan_price = int(price3)
                        total = int(price3)+int(sim_price)
                        tax = total/10
                        bill= tax+total
                        return[SlotSet("tax",tax),SlotSet("plan_price",plan_price),SlotSet("total_price",bill),SlotSet("plan_detail",detail),FollowupAction("confirm_plan_selection_form")]
                else:
                    dispatcher.utter_message(text=f"Error: {response_desc}")
                    dispatcher.utter_message(template="utter_menu2")
                    return [AllSlotsReset(),Restarted()]
            except Exception as e:
                dispatcher.utter_message(text="An error occurred while processing. Please try again later.")
                dispatcher.utter_message(template="utter_menu2")
                return [AllSlotsReset(),Restarted()]

# confirming the bill            
class ValidatePlanSelectionForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_confirm_plan_selection_form"
    def validate_confirm_plan(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[str, str],
    ) -> Dict[str, str]:
        intent = tracker.get_intent_of_latest_message()
        decision = tracker.get_slot("confirm_plan")

        if not decision:
            dispatcher.utter_message(text="Invalid input.")
            return {"confirm_plan": None}
        if decision is not None:
            if intent in ["affirm", "deny"]:
                return {"confirm_plan": intent}
            else:
                dispatcher.utter_message(text="Invalid input.")
                return {"confirm_plan": None}

# if confirmed then asking for number            
class ActionsubmitPlanForm(Action):
    def name(self) -> Text:
        return "action_submit_plan_form"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
       domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        confirmation = tracker.get_slot("confirm_plan")
        if confirmation=="affirm":
            return[FollowupAction("number_form")]
        else:
            dispatcher.utter_message(text="Your Order has been cancelled")
            dispatcher.utter_message(template="utter_menu2")
            return [AllSlotsReset(),Restarted()]

class ValidateNumberForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_number_form"
    def validate_number_option(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[str, str],
    ) -> Dict[str, str]:
        intent = tracker.get_intent_of_latest_message()
        print(intent)
        if intent =="enter_number":
            return {"number_option":"number"}
        elif intent == "user_change":
           return {"number_option":"new_number"}
        else:
            dispatcher.utter_message(text="Invalid input")
            return{"number_option": None}
           
class ActionSubmitNumberForm(Action):
    def name(self) -> Text:
        return "action_submit_number_form"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
       domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        number_option = tracker.get_slot("number_option")
        if number_option=="number":
            return[FollowupAction("sim_number_form")]   
        elif number_option=="new_number":
            try:
                api_url =f"http://127.0.0.1:5000/api/user/get?channel=web&input=NEW_NUM"
                response = requests.get(api_url)
                user_data = response.json()
                response_code = user_data.get("responseCode", 500)  
                response_desc = user_data.get("responseDesc", "Unknown error")

                if response_code == 200 and response_desc == "Success":
                    number = user_data.get("number")
                    number = str(number)
                    return [SlotSet("sim_number",number),FollowupAction("sim_number_form")]     
                else:
                    dispatcher.utter_message(text=f"Error: {response_desc}")
                    dispatcher.utter_message(template="utter_menu2")
                    return [AllSlotsReset(),Restarted()]
            except Exception as e:
                dispatcher.utter_message(text="An error occurred while processing. Please try again later.")
                dispatcher.utter_message(template="utter_menu2")
                return [AllSlotsReset(),Restarted()]
class ValidateSimNumberForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_sim_number_form"

    def validate_sim_number(
        self,
        slot_value:Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate 'account_number' value."""
        num = tracker.get_slot("sim_number")
    

        if not num.isdigit() or len(num) != 10:
            dispatcher.utter_message(text="Invalid phone number.")
            return {"sim_number": None}
        else:
            return {"sim_number": num}
        
    def validate_confirm_sim_number(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[str, str],
    ) -> Dict[str, str]:
        intent = tracker.get_intent_of_latest_message()
        decision = tracker.get_slot("confirm_sim_number")

        if not decision:
            dispatcher.utter_message(text="Invalid input.")
            return {"confirm_sim_number": None}
        if decision is not None:
            if intent in ["affirm", "deny"]:
                return {"confirm_sim_number": intent}
            else:
                dispatcher.utter_message(text="Invalid input.")
                return {"confirm_sim_number": None}
            
class ActionsubmitsimNUmberForm(Action):
    def name(self) -> Text:
        return "action_submit_sim_number_form"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
       domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        confirmation = tracker.get_slot("confirm_sim_number")
        if confirmation=="affirm":
            dispatcher.utter_message(text="Enter the following details")
            return[FollowupAction("address_form")]
        else:
            dispatcher.utter_message(text="Your Order has been cancelled")
            dispatcher.utter_message(template="utter_menu2")
            return [AllSlotsReset(),Restarted()]
                
class ValidateAddressForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_address_form"

    def validate_name(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[str, str],
    ) -> Dict[str, str]:
        name = tracker.get_slot("buyer_name")

        if not name:
            dispatcher.utter_message(text="This field can't be empty.")
            return {"buyer_name": None}
        else:
            return {"buyer_name": value}

    def validate_buyer_email(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[str, str],
    ) -> Dict[str, str]:
        email = value.strip()  
    
        if not email:
            dispatcher.utter_message(text="Email is missing.")
            return {"buyer_email": None}
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    
        if not re.match(pattern, email):
            dispatcher.utter_message(text="Invalid Email.")
            return {"buyer_email": None}
        else:
            return {"buyer_email": email}
    
    def validate_address(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[str, str],
    ) -> Dict[str, str]:
        address = tracker.get_slot("address")

        if not address:
            dispatcher.utter_message(text="This field can't be empty.")
            return {"address": None}
        else:
            return {"address": value}

    def validate_confirm_address(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[str, str],
    ) -> Dict[str, str]:
        intent = tracker.get_intent_of_latest_message()
        decision = tracker.get_slot("confirm_address")

        if not decision:
            dispatcher.utter_message(text="Invalid input.")
            return {"confirm_address": None}
        if decision is not None:
            if intent in ["affirm", "deny"]:
                return {"confirm_address": intent}
            else:
                dispatcher.utter_message(text="Invalid input.")
                return {"confirm_address": None}


class ActionsubmitAddressForm(Action):
    def name(self) -> Text:
        return "action_submit_address_form"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
       domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        confirmation = tracker.get_slot("confirm_address")
        if confirmation=="affirm":
            return[FollowupAction("bill_form")]

        else:
            dispatcher.utter_message(text="Your Order has been cancelled")
            dispatcher.utter_message(template="utter_menu2")
            return [AllSlotsReset(),Restarted()]

class ValidateBillForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_bill_form"
    
    def validate_confirm_bill(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[str, str],
    ) -> Dict[str, str]:
        intent = tracker.get_intent_of_latest_message()
        decision = tracker.get_slot("confirm_bill")

        if not decision:
            dispatcher.utter_message(text="Invalid input.")
            return {"confirm_bill": None}
        if decision is not None:
            if intent in ["affirm", "deny"]:
                return {"confirm_bill": intent}
            else:
                dispatcher.utter_message(text="Invalid input.")
                return {"confirm_bill": None}

class ActionsubmitBillForm(Action):
    def name(self) -> Text:
        return "action_submit_bill_form"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
       domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        confirmation = tracker.get_slot("confirm_bill")
        if confirmation=="affirm":
            dispatcher.utter_message(text="Add Payment Details")
            return[FollowupAction("payment_form")]

        else:
            dispatcher.utter_message(text="Your Order has been cancelled")
            dispatcher.utter_message(template="utter_menu2")
            return [AllSlotsReset(),Restarted()]

class ValidatePaymentForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_payment_form"
    def validate_card_number(
        self,
        slot_value:Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate 'account_number' value."""
        num = tracker.get_slot("card_number")
        if not num.isdigit() or len(num) != 16:
            dispatcher.utter_message(text="Invalid card number.")
            return {"card_number": None}
        else:
            return {"card_number": num}
        
    def validate_name_on_card(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[str, str],
    ) -> Dict[str, str]:
        name = tracker.get_slot("name_on_card")
        if not name:
            dispatcher.utter_message(text="This field can't be empty.")
            return {"name_on_card": None}
        else:
            return {"name_on_card": value}

    def validate_expiry(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[str, str],
    ) -> Dict[str, str]:
        expiry = tracker.get_slot("expiry")
        if not expiry:
            dispatcher.utter_message(text="This field can't be empty.")
            return {"expiry": None}
        else:
            if expiry[2]== "/" and int(expiry[3])>=2 and int(expiry[4])>=4:
                return {"expiry": expiry}
            else:
                dispatcher.utter_message(text="Invalid Expiry. Format of expiry date should be MM/YY")
                return {"expiry": None}

    def validate_cvv(
        self,
        slot_value:Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate 'account_number' value."""
        cvv = tracker.get_slot("cvv")
        if not cvv.isdigit() or len(cvv) != 3:
            dispatcher.utter_message(text="Invalid CVV.")
            return {"cvv": None}
        else:
            return {"cvv": cvv}
    
    def validate_confirm_order(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[str, str],
    ) -> Dict[str, str]:
        intent = tracker.get_intent_of_latest_message()
        decision = tracker.get_slot("confirm_order")

        if not decision:
            dispatcher.utter_message(text="Invalid input.")
            return {"confirm_order": None}
        if decision is not None:
            if intent in ["affirm", "deny"]:
                return {"confirm_order": intent}
            else:
                dispatcher.utter_message(text="Invalid input.")
                return {"confirm_order": None}
    
class ActionsubmitPaymentForm(Action):
    def name(self) -> Text:
        return "action_submit_payment_form"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
       domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        confirmation = tracker.get_slot("confirm_order")
        if confirmation=="affirm":
            dispatcher.utter_message(template="utter_submit")
            dispatcher.utter_message(template="utter_menu2")
            return [AllSlotsReset(),Restarted()]

        else:
            dispatcher.utter_message(text="Your Order has been cancelled")
            dispatcher.utter_message(template="utter_menu2")
            return [AllSlotsReset(),Restarted()]

class ValidateRaiseTicketForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_ticket_form"

    def validate_name(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[str, str],
    ) -> Dict[str, str]:
        name = tracker.get_slot("name")

        if not name:
            dispatcher.utter_message(text="This field can't be empty.")
            return {"name": None}
        else:
            return {"name": value}

    def validate_phone_number(
        self,
        slot_value:Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate 'account_number' value."""
        num = tracker.get_slot("phone_number")
    

        if not num.isdigit() or len(num) != 10:
            dispatcher.utter_message(text="Invalid phone number.")
            return {"phone_number": None}
        else:
            return {"phone_number": num}
    
        
    def validate_issue_message(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[str, str],
    ) -> Dict[str, str]:
        issue = tracker.get_slot("issue_message")
        if not issue:
            dispatcher.utter_message(text="This field can't be empty.")
            return {"issue_message": None}
        else:
            return {"issue_message": value}

    def validate_email(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[str, str],
    ) -> Dict[str, str]:
        email = value.strip()  
    
        if not email:
            dispatcher.utter_message(text="Email address is missing.")
            return {"email": None}
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    
        if not re.match(pattern, email):
            dispatcher.utter_message(text="Invalid email address.")
            return {"email": None}
        else:
            return {"email": email}

    def validate_confirm_details(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[str, str],
    ) -> Dict[str, str]:
        intent = tracker.get_intent_of_latest_message()
        decision = tracker.get_slot("confirm_details")
        accNum = tracker.get_slot("phone_number")

    
        if not decision:
            dispatcher.utter_message(text="Invalid input.")
            return {"confirm_details": None}
        if decision is not None:
            if intent in ["affirm", "deny"]:
                return {"confirm_details": intent}
            else:
                dispatcher.utter_message(text="Invalid input.")
                return {"confirm_details": None}
    
        
class ActionSubmitTicketForm(Action):
    def name(self) -> Text:
        return "action_submit_ticket_form"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
       domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        global ticketCount
        name = tracker.get_slot("name")
        accNum = tracker.get_slot("phone_number")
        email = tracker.get_slot("email")
        issue = tracker.get_slot("issue_message")
        confirmation = tracker.get_slot("confirm_details")
        confirmation2 = tracker.get_slot("confirm_details_info")
        accType = tracker.get_slot("account_type")
          # Construct the URL for your REST API
        api_url = f"http://127.0.0.1:5000/api/user/put?input=RAISE_TICKET"
        data = {
            'Name': name,
            'Phone_Number': accNum,
            'Email': email,
            "Issue": issue
        }
        if confirmation == "affirm":
            try:
                api_url2 =f"http://127.0.0.1:5000/api/user/get?msisdn={accNum}&channel=web&input=ACC_TYPE"
                response2 = requests.get(api_url2)
                user_data2 = response2.json()
                response_code = user_data2.get("responseCode", 500)  
                response_desc = user_data2.get("responseDesc", "Unknown error")

                if response_code == 200 and response_desc == "Success":
                    acc_type = user_data2.get("Type")
                else:
                    dispatcher.utter_message(text=f"Error: {response_desc}")
                    return[SlotSet("latest_intent", "greet"),FollowupAction("action_submit_info_form")]
                
                response = requests.put(api_url, json=data)
                user_data = response.json()
                response_code = user_data.get("responseCode", 500)  
                response_desc = user_data.get("responseDesc", "Unknown error")
                message = user_data.get("message")

                if response_code == 200 and response_desc == "success":
                    ticketCount=1
                    dispatcher.utter_message(text=f"{message}")
                    dispatcher.utter_message(template="utter_menu2")
                    return [SlotSet("account_type", acc_type),SlotSet("name", None),SlotSet("email", None),SlotSet("issue_message", None),SlotSet("confirm_details", None),SlotSet("latest_intent", "greet"),SlotSet("confirm_details_info","affirm")]
                else:
                    dispatcher.utter_message(text=f"Error: {response_desc}, code : {response_code}")
                    dispatcher.utter_message(template="utter_menu2")
                    return [SlotSet("account_type", acc_type),SlotSet("name", None),SlotSet("email", None),SlotSet("issue_message", None),SlotSet("confirm_details", None),SlotSet("latest_intent", "greet"),SlotSet("confirm_details_info","affirm")]
            except Exception as e:
                dispatcher.utter_message(text="An error occurred while processing. Please try again later.") 
                dispatcher.utter_message(template="utter_menu2")
                return [SlotSet("account_type", acc_type),SlotSet("name", None),SlotSet("email", None),SlotSet("issue_message", None),SlotSet("confirm_details", None),SlotSet("latest_intent", "greet"),SlotSet("confirm_details_info","affirm")]

        else:
            ticketCount=0
            dispatcher.utter_message(text="Request Cancelled.") 
            dispatcher.utter_message(template="utter_menu2")
            if confirmation2 == "affirm":
                return [SlotSet("name", None),SlotSet("email", None),SlotSet("issue_message", None),SlotSet("confirm_details", None),SlotSet("latest_intent", "greet")]
            else:
                return [SlotSet("name", None),SlotSet("phone_number", None),SlotSet("account_type", None), SlotSet("email", None),SlotSet("issue_message", None),SlotSet("confirm_details", None),SlotSet("latest_intent", "greet"),SlotSet("confirm_details_info",None)]

class ValidateInformationForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_info_form"

    def validate_phone_number(
        self,
        slot_value:Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate 'account_number' value."""
        num = tracker.get_slot("phone_number")
    

        if not num.isdigit() or len(num) != 10:
            dispatcher.utter_message(text="Invalid phone number.")
            return {"phone_number": None}
        else:
            return {"phone_number": num}
        
    def validate_confirm_details_info(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[str, str],
    ) -> Dict[str, str]:
        intent = tracker.get_intent_of_latest_message()
        decision = tracker.get_slot("confirm_details_info")

        if not decision:
            dispatcher.utter_message(text="Invalid input.")
            return {"confirm_details_info": None}
        if decision is not None:
            if intent in ["affirm", "deny"]:
                return {"confirm_details_info": intent}
            elif decision=="affirm":
                return {"confirm_details_info": decision}
            else:
                dispatcher.utter_message(text="Invalid input.")
                return {"confirm_details_info": None}
            

class ActionSubmitInformationForm(Action):
    def name(self) -> Text:
        return "action_submit_info_form"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
       domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        accType = tracker.get_slot("account_type")
        accNum = tracker.get_slot("phone_number")
        intent = tracker.get_slot("latest_intent")
        confirmation = tracker.get_slot("confirm_details_info")
        if confirmation== "affirm":
            if accType!=None:
                if intent== "check_balance":
                    return[FollowupAction("action_balance_enquiry")]
                elif intent== "transaction":
                    return[FollowupAction("action_transaction_enquiry")]
                elif intent=="ticket_status":
                    return[FollowupAction("action_ticket_status")]
                else:
                    dispatcher.utter_message(template="utter_menu2")
                 
            else:
                return[FollowupAction("action_find_acc")]
        else:
            dispatcher.utter_message(template="utter_menu2")  
            return[AllSlotsReset(),Restarted()]

        
class ActionBalanceEnquiry(Action):
    def name(self) -> Text:
        return "action_balance_enquiry"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
       domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        accType = tracker.get_slot("account_type")
        accNum = tracker.get_slot("phone_number")
        confirmation = tracker.get_slot("confirm_details_info")
        intent= tracker.get_intent_of_latest_message()

        try:
            if accType!= None and accNum!= None and confirmation=="affirm":
                api_url =f"http://127.0.0.1:5000/api/user/get?msisdn={accNum}&channel=web&input=BALANCE_ENQUIRY"
                response = requests.get(api_url)
                user_data = response.json()
                response_code = user_data.get("responseCode", 500)  
                response_desc = user_data.get("responseDesc", "Unknown error")

                if response_code == 200 and response_desc == "Success":
                    balance = user_data.get("BALANCE", "N/A")
                    validity = user_data.get("VALIDITY","N/A")
                    dispatcher.utter_message(text=f"Your account balance is {balance}.\nValid until {validity}.")
                    dispatcher.utter_message(template="utter_menu2")
                    return[SlotSet("latest_intent", "greet")]
                else:
                    dispatcher.utter_message(text=f"Error: {response_desc}")
                    dispatcher.utter_message(template="utter_menu2")
                    return[SlotSet("latest_intent", "greet")]
            else : 
                return[FollowupAction('info_form'),SlotSet("latest_intent", intent)]
    
        except Exception as e:
            dispatcher.utter_message(text="An error occurred while fetching the balance. Please try again later.")  
            dispatcher.utter_message(template="utter_menu2")
            return[SlotSet("latest_intent", "greet")]


class ActionTransactionEnquiry(Action):
    def name(self) -> Text:
        return "action_transaction_enquiry"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
       domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        accType = tracker.get_slot("account_type")
        accNum = tracker.get_slot("phone_number")
        intent= tracker.get_intent_of_latest_message()
        confirmation = tracker.get_slot("confirm_details_info")

        try:
            if accType!= None and accNum!= None and confirmation=="affirm":
                api_url =f"http://127.0.0.1:5000/api/user/get?msisdn={accNum}&channel=web&input=TRANSACTION_ENQUIRY"
                response = requests.get(api_url)
                user_data = response.json()
                response_code = user_data.get("responseCode", 500)  
                response_desc = user_data.get("responseDesc", "Unknown error")

                if response_code == 200 and response_desc == "Success":
                    history1 = user_data.get("Transaction 1")
                    history2 = user_data.get("Transaction 2")
                    history3 = user_data.get("Transaction 3")
                    history4 = user_data.get("Transaction 4")
                    history5 = user_data.get("Transaction 5")
                    dispatcher.utter_message(text=f"Your last 5 call history are:\n{history1}\n{history2}\n{history3}\n{history4}\n{history5}")
                    dispatcher.utter_message(template="utter_menu2")
                    return[SlotSet("latest_intent", "greet")]

                else:
                    dispatcher.utter_message(text=f"Error: {response_desc}")
                    dispatcher.utter_message(template="utter_menu2")
                    return[SlotSet("latest_intent", "greet")]
            else : 
                return[FollowupAction('info_form'),SlotSet("latest_intent", intent)]
        
        except Exception as e:
            dispatcher.utter_message(text="An error occurred while fetching the history. Please try again later.")  
            dispatcher.utter_message(template="utter_menu2")
            return[SlotSet("latest_intent", "greet")]
        

class ActionTicketStatus(Action):
    def name(self) -> Text:
        return "action_ticket_status"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
       domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        accType = tracker.get_slot("account_type")
        accNum = tracker.get_slot("phone_number")
        intent= tracker.get_intent_of_latest_message()
        confirmation = tracker.get_slot("confirm_details_info")

        try:
            if accType!= None and accNum!= None and confirmation=="affirm":
                api_url =f"http://127.0.0.1:5000/api/user/get?msisdn={accNum}&channel=web&input=TICKET_STATUS"
                response = requests.get(api_url)
                user_data = response.json()
                response_code = user_data.get("responseCode", 500)  
                response_desc = user_data.get("responseDesc", "Unknown error")

                if response_code == 200 and response_desc == "Success":
                    if ticketCount==0:
                        description = user_data.get("description1")
                        dispatcher.utter_message(text=f"{description}")
                    else:
                        description = user_data.get("description2")
                        dispatcher.utter_message(text=f"{description}")

                    dispatcher.utter_message(template="utter_menu2")
                    return[SlotSet("latest_intent", "greet")]

                else:
                    dispatcher.utter_message(text=f"Error: {response_desc}")
                    dispatcher.utter_message(template="utter_menu2")
                    return[SlotSet("latest_intent", "greet")]
            else:
                return[FollowupAction('info_form'),SlotSet("latest_intent", intent)]
        
        except Exception as e:
            dispatcher.utter_message(text="An error occurred while fetching the status. Please try again later.")  
            dispatcher.utter_message(template="utter_menu2")
            return[SlotSet("latest_intent", "greet")]
        

class ActionChangeInfo(Action):
    def name(self) -> Text:
        return "action_change_info"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
       domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        intent = tracker.get_intent_of_latest_message()
        global ticketCount
        if intent== "user_change":
            ticketCount=0
            return [FollowupAction("info_form"),SlotSet("phone_number",None),SlotSet("account_type",None),SlotSet("confirm_details_info",None)]

class ActionFindACC(Action):
    def name(self) -> Text:
        return "action_find_acc"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
       domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        num = tracker.get_slot("phone_number")
        try:
            if num!= None:
                    api_url =f"http://127.0.0.1:5000/api/user/get?msisdn={num}&channel=web&input=ACC_TYPE"
                    response = requests.get(api_url)
                    user_data = response.json()
                    response_code = user_data.get("responseCode", 500)  
                    response_desc = user_data.get("responseDesc", "Unknown error")

                    if response_code == 200 and response_desc == "Success":
                        acc_type = user_data.get("Type")
                        return[SlotSet("account_type", acc_type),FollowupAction("action_submit_info_form")]

                    else:
                        dispatcher.utter_message(text=f"Error: {response_desc}")
                        return[SlotSet("latest_intent", "greet"),FollowupAction("action_submit_info_form")]
            else:
                    return[FollowupAction('info_form')]
        
        except Exception as e:
            dispatcher.utter_message(text="An error occurred while fetching the subscriber detail. Please try again later.")  
            return[SlotSet("latest_intent", "greet")]