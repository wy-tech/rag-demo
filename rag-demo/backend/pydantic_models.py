from typing import Literal, List
from langchain_core.pydantic_v1 import BaseModel, Field

class CardTypeFilter(BaseModel):
    card_type: List[Literal["visa_classic","visa_gold","visa_infinite","visa_platinum","visa_signature","any"]] = Field(
        ...,
        description="Given a user query, output the VISA card type only if the customer explicitly mentions that they are holding it: Visa Classic, Visa Gold, Visa Infinite, Visa Platinum, Visa Signature. Do not infer the card type just because the customer has a card. If there is no information about the card type, output False.",
    )

class PaymentTypeFilter(BaseModel):
    payment_type: Literal["debit","credit","any"] = Field(
        ...,
        description="Given a customer query, output the payment type only if the customer explicitly mentions about payment: debit, credit. Do not infer the payment type just because the customer has a card. If there is no information about the payment type, output any.",
    )