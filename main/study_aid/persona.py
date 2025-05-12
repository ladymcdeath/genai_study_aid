from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
import prompts

# Function to create Conversational Agent
def create_conversational_agent(llm, vector_db):

    retriever = vector_db.as_retriever()

    prompt = PromptTemplate(
        input_variables=["context", "chat_history", "question"],
        template=prompts.persona_template
    )

    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        k=4,  # keeps 4 recent exchanges
        return_messages=True
    )

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        verbose=False
    )

    return qa_chain