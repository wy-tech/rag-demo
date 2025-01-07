import datetime

from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from backend.pydantic_models import CardTypeFilter, PaymentTypeFilter
from backend.utils import get_unique_union, convert_to_langchain_history
from backend.vector_store import setup_vector_store

vector_store = setup_vector_store()
# LLM with function call 
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
target_k = 4

def get_card_type(state):

    question = state.get("question")
    system = """
    You are an expert at deciding the customer's card type, or they did not specify. The customer query may be long, so be detailed and decide on any relevant information they provided.

    If customer specifies their preference for VISA classic, VISA gold, VISA inifinite, VISA platinum or VISA signature card, output the card type. In all other cases, output any. Never infer the card type.

    If customer looks for other card types except the ones they mention, you may infer.

    Only these outputs are allowed: visa_classic, visa_gold, visa_infinite, visa_platinum, visa_signature, any. If multiple of the mentioned outputs are valid, output them as comma separated strings. Never output any other values.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{question}"),
        ]
    )
    structured_card_type_llm = llm.with_structured_output(CardTypeFilter)
    structured_query_analyzer_card_type = prompt | structured_card_type_llm
    card_types = structured_query_analyzer_card_type.invoke(question)
    return {"card_type": card_types.card_type}

def get_card_type(state):

    question = state.get("question")
    system = """
    You are an expert at deciding the customer's card type, or they did not specify. The customer query may be long, so be detailed and decide on any relevant information they provided.

    If customer specifies their preference for VISA classic, VISA gold, VISA inifinite, VISA platinum or VISA signature card, output the card type. In all other cases, output any. Never infer the card type.

    If customer looks for other card types except the ones they mention, you may infer.

    Only these outputs are allowed: visa_classic, visa_gold, visa_infinite, visa_platinum, visa_signature, any. If multiple of the mentioned outputs are valid, output them as comma separated strings. Never output any other values.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{question}"),
        ]
    )
    structured_card_type_llm = llm.with_structured_output(CardTypeFilter)
    structured_query_analyzer_card_type = prompt | structured_card_type_llm
    card_types = structured_query_analyzer_card_type.invoke(question)
    return {"card_type": card_types.card_type}

def get_payment_type(state):

    question = state.get("question")
    system = """
    You are an expert at deciding if customers want to pay by debit, credit, or they did not specify. The customer query may be long, so be detailed and decide on any relevant information they provided.
    
    If customer specifies their preference for debit or credit, output the payment type. In all other cases, output any. Never infer the payment type.

    If customer looks for other payment types except the ones they mention, you may infer.

    Only these outputs are allowed: debit, credit, any.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{question}"),
        ]
    )
    structured_payment_type_llm = llm.with_structured_output(PaymentTypeFilter)
    structured_query_analyzer_payment_type = prompt | structured_payment_type_llm
    payment_type = structured_query_analyzer_payment_type.invoke(question)
    return {"payment_type": payment_type.payment_type}

def construct_filter(state):
    metadata_to_filter = {"visa_classic":"cardProduct_Visa Classic",
                        "visa_gold":"cardProduct_Visa Gold",
                        "visa_infinite":"cardProduct_Visa Infinite",
                        "visa_platinum":"cardProduct_Visa Platinum",
                        "visa_signature":"cardProduct_Visa Signature",
                        "debit":"paymentType_Debit",
                        "credit":"paymentType_Credit",
                        }
    
    payment_type = state.get("payment_type")
    card_type = state.get("card_type")

    types = []
    if "any" not in payment_type:
        types.extend(payment_type)
    if "any" not in card_type:
        types.append(card_type)
    
    filter_list = []
    for t in types:
        filter_list.append({metadata_to_filter[t]: {'$eq':True}})
    return {"filter_list":filter_list}


def filter_parallel(state):
    question = state.get("question")
    map_chain = RunnableParallel(payment_type=get_payment_type,card_type=get_card_type)
    res = map_chain.invoke({"question":question})
    payment_type = res["payment_type"]["payment_type"]
    card_type = res["card_type"]["card_type"]

    metadata_to_filter = {"visa_classic":"cardProduct_Visa Classic",
                        "visa_gold":"cardProduct_Visa Gold",
                        "visa_infinite":"cardProduct_Visa Infinite",
                        "visa_platinum":"cardProduct_Visa Platinum",
                        "visa_signature":"cardProduct_Visa Signature",
                        "debit":"paymentType_Debit",
                        "credit":"paymentType_Credit",
                        }
    types = []
    if payment_type != "any":
        types.append(payment_type)
    if "any" not in card_type:
        types.extend(card_type)
    filter_list = []
    for t in types:
        filter_list.append({metadata_to_filter[t]: {'$eq':True}})
    return {"filter_list":filter_list}



def multi_query_retriever(state):
    filter_list = state.get("filter_list")
    question = state.get("question")
    # filter_list = [{'paymentType_Credit': {'$eq': True}},
    #                {'cardProduct_Visa Classic': {'$eq': True}}]
    # question = {"i want eat with visa classic and credit card"}
    
    filter_dict = {'$and': filter_list}
    
    # Multi Query: Different Perspectives
    template = """You are an AI language model assistant. Your task is to generate five 
    different versions of the given user question to retrieve relevant documents from a vector 
    database. By generating multiple perspectives on the user question, your goal is to help
    the user overcome some of the limitations of the distance-based similarity search. 
    Provide these alternative questions separated by newlines. Original question: {question}"""
    prompt_perspectives = ChatPromptTemplate.from_template(template)

    generate_queries = (
    prompt_perspectives 
    | llm
    | StrOutputParser() 
    | (lambda x: x.split("\n"))
    )

    if not filter_list:
        retriever = vector_store.as_retriever(search_kwargs={"k": target_k})
    else:
        retriever = vector_store.as_retriever(search_kwargs={"k": target_k,
                                            "filter":filter_dict})
    
    # Retrieve
    retrieval_chain = generate_queries | retriever.map() | get_unique_union
    docs = retrieval_chain.invoke({"question":question})
    return {"multi_query_docs": docs}

    # return docs



def decomposition_retriever(state):
    filter_list = state.get("filter_list")
    question = state.get("question")
    # filter_list = [{'paymentType_Credit': {'$eq': True}},
    #                {'cardProduct_Visa Classic': {'$eq': True}}]
    # question = {"i want eat with visa classic and credit card. i want to eat and shop and releax"}
    
    filter_dict = {'$and': filter_list}
    
    # Decomposition
    template = """You are a helpful assistant that breaks down an input question into its sub-questions. \n
    The goal is to break down the input into a set of sub-problems / sub-questions that can be answers in isolation. \n
    You must not fluff up or decorate the sub-questions. \n
    Generate multiple search queries related to: {question} \n
    Output (3 queries):"""
    prompt_decomposition = ChatPromptTemplate.from_template(template)

    generate_queries_decomposition = ( 
        prompt_decomposition 
        | llm 
        | StrOutputParser() 
        | (lambda x: x.split("\n")))

    if not filter_list:
        retriever = vector_store.as_retriever(search_kwargs={"k": target_k})
    else:
        retriever = vector_store.as_retriever(search_kwargs={"k": target_k,
                                            "filter":filter_dict})
    # Retrieve
    retrieval_chain = generate_queries_decomposition | retriever.map() | get_unique_union
    docs = retrieval_chain.invoke({"question":question})
    return {"decomposition_docs": docs}
    # return docs


def generate(state):
    decomposition_docs = state.get("decomposition_docs")
    multi_query_docs = state.get("multi_query_docs")
    question = state.get("question")
    history = state.get("history")

    # Example st.session_state.messages
    # st.session_state.messages = [
    #     {"role": "human", "content": "Hello!"},
    #     {"role": "ai", "content": "Hi there! How can I help you?"},
    # ]

    history = convert_to_langchain_history(history)
    context = get_unique_union([decomposition_docs,multi_query_docs])
    # Prompt
    template = """You are an AI Assistant who answers questions for VISA card offers. 
    Suggest as many activities as possible that may satisfy the customer's needs. Provide adequate information about the offer and commmunicate in an easy-to-read manner. 

    If you are unable to help, politely say so.

    You may use the chat history if the customer requires it:
    {history}
    
    Answer based only on the chat history and the following context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    rag_chain = LLMChain(llm=llm, prompt=prompt)
    return {"generation": rag_chain.run({"context": context, "question": question, "history": history})}