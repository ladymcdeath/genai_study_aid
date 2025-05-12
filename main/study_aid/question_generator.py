from langchain.prompts import PromptTemplate
import re,json
from langchain.chains.summarize import load_summarize_chain
import prompts

def generate_prompt(prompt):
    question_prompt = PromptTemplate(
        input_variables=["text"],
        template=prompt
    )
    return question_prompt

def extract_questions(text):
    # Find all blocks that start with [ and end with ]
    blocks = re.findall(r'\[\s*{.*?}\s*\]', text, re.DOTALL)
    # Find all blocks that start with { and end with }
    objs = re.findall(r'\{.*?\}', blocks[0], re.DOTALL)
    questions = []

    # Skipping malformed json in the output
    for obj in objs:
        # Safely evaluate the string into a Python dictionary
        try:
            q = json.loads(obj.strip())

        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            q = []

        questions.append(q)

    return questions

def quiz_generator(llm, docs):

    question_prompt = generate_prompt(prompts.QUESTION_GEN_PROMPT)

    chain = load_summarize_chain(
        llm=llm,
        chain_type="stuff",  # Use 'stuff' to process each chunk independently
        prompt=question_prompt,
        verbose=False
    )

    questions_all = []

    # Loop through each chunk
    for idx, doc in enumerate(docs):
        result = chain.invoke([doc])
        output_text = result.get('output_text', 'No questions generated')
        # Cleaning the output
        questions = extract_questions(output_text)
        questions_all.extend(questions)

    valid_questions = [q for q in questions_all if isinstance(q, dict)]
    mcq_questions = [q for q in valid_questions if q.get("type") == "mcq"]
    short_questions = [q for q in valid_questions if q.get("type") == "short"]

    return mcq_questions, short_questions

