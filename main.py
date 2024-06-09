from dotenv import load_dotenv
import sys
import google.generativeai as genai
import re
import os
import zipfile
from tqdm import tqdm

load_dotenv()

# Function to setup Gemini AI API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    safety_settings=[
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE", "probability":"BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE", "probability":"BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE", "probability":"BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE", "probability":"BLOCK_NONE"},
    ],
)

def to_markdown(text):
  text = text.replace('*', '').replace('#', '')
  return text

def extract_question_list(text):
    lines = text.split('\n')

    # Extract lines starting with a number
    extracted_lines = [line.strip() for line in lines if line.strip().startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9', '0'))]
    return extracted_lines

def extract_project_structure(text, marker="└── "):
    # Use regular expression to find content within triple backticks
    matches = re.findall(r"```(.*?)```", text, re.DOTALL)
    for match in matches:
        if marker in match:
            return f"```{match}```"
    return ""


def extract_code_block(text):
    matches = re.findall(r"```(.*?)```", text, re.DOTALL)
    for match in matches:
        return f"```{match}```"
    return ""


def extract_file_list(file_structure):
    file_structure = file_structure.replace("│", " ")
    # Extract the section containing the file structure

    file_list = []
    path_stack = []

    for line in file_structure.split("\n"):
        # Skip empty lines
        if not line.strip():
            continue

        # Remove leading spaces and tree symbols
        clean_line = line.lstrip().replace("└──", "").replace("├──", "").strip()

        # Calculate the depth of the current line
        depth = (len(line) - len(line.lstrip())) // 4

        # If depth is less than the length of the stack, pop from the stack
        while len(path_stack) > depth:
            path_stack.pop()

        # If it's a directory (no file extension), push to stack
        if "." not in clean_line:
            path_stack.append(clean_line)
        else:
            # Construct the full path
            full_path = "/".join(path_stack + [clean_line])
            file_list.append(full_path)

    return file_list

# Function to interact with Gemini AI API
def call_gemini_api(prompt):
    response = model.generate_content(prompt, safety_settings=[
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE", "probability":"BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE", "probability":"BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE", "probability":"BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE", "probability":"BLOCK_NONE"},
    ],)
    return to_markdown(response.text)


def get_project_structure(user_project_description, previous_questions_and_answers):
    prompt = f"""
    You are an expert software developer. Based on the following project description and questions answers related to the project, generate a complete project file structure:

    Project Description: {user_project_description}

    Questions Answers Related To The Project: 
    {previous_questions_and_answers}

    Please provide only the project file structure with a maximum of 20 files. Ensure the structure includes only the files that need to be created or modified, without generating any code.
    """

    return call_gemini_api(prompt)

def get_all_quesetions(user_project_description):
    prompt = f"""
    You are an expert software developer. Based on the following project description, please generate a list of clarifying questions to ensure a comprehensive understanding of the project requirements:

    Project Description: {user_project_description}

    Please generate questions that would help in understanding the project details. Structure your questions as follows:
    [Number] [Category of question related to project]: [Question]

    Ensure that all questions within the same category are combined or concatenated into exactly one question as a single line with a maximum of 10 questions.
    """
    return call_gemini_api(prompt)

def get_project_qus(user_project_description, previous_questions_and_answers, qus_answer):
    prompt = f"""
    You are an expert software developer. Based on the following project description, please generate a list of clarifying questions to ensure a comprehensive understanding of the project requirements:

    Project Description: {user_project_description}

    Please generate questions that would help in understanding the project details. Structure your questions as follows:
    [Number] [Category of question related to project]: [Question]

    Ensure that all questions within the same category are combined or concatenated into exactly one question as a single line.

    Previous Questions and Answers:
    {previous_questions_and_answers}

    Specify below the question numbers for which you've already provided answers (if any):
    {qus_answer}

    Now, please ask any clarifying questions from above unanswered questions if needed.
    Ensure that you donot generate the questiones that I have already answered even if the answer is wrong.
    """
    return call_gemini_api(prompt)

def parse_project_structure(project_structure):
    directories = project_structure.strip().split("\n")
    files = []
    for directory in directories:
        # Skip empty lines
        if directory.strip() == "":
            continue
        # Add files within the directory
        files.append(f"{directory}/")
    return files


def get_project_file(user_project_description, project_structure, file_path, previous_questions_and_answers):
    prompt = f"""
    You are an expert software developer. Based on the following project description, questions answers related to the project and file structure, generate the code for the specified file:
    
    Project Description: {user_project_description}

    Questions Answers Related To The Project: 
    {previous_questions_and_answers}
    
    Project File Structure:
    {project_structure}

    File to Generate Code For: {file_path}

    Please provide only the code for the specified file without generating anything else.
    """

    return extract_code_block(call_gemini_api(prompt))


def create_directory_and_files(
    directory_name, file_list, user_project_description, project_structure, previous_questions_and_answers
):
    # Create the directory
    directory_path = os.path.join(os.getcwd(), directory_name)
    os.makedirs(directory_path, exist_ok=True)

    # Create each file inside the directory and write content to it
    for file_path in tqdm(file_list, desc="Creating files", unit="file"):
        # Extract the directory path from the file path
        file_directory = os.path.dirname(file_path)
        # Create intermediate directories if they don't exist
        os.makedirs(os.path.join(directory_path, file_directory), exist_ok=True)
        # Create and write content to the file
        with open(os.path.join(directory_path, file_path), "w") as file:
            file_content_with_extention = get_project_file(
                user_project_description, project_structure, file_path, previous_questions_and_answers
            )
            print("\n\nCode Generated for the file: "+file_path)
            print(file_content_with_extention)
            file_content = re.sub(
                r"^```.*?$",
                "",
                file_content_with_extention,
                flags=re.MULTILINE | re.DOTALL,
            )
            file.write(file_content)

    # Zip the directory
    zip_file_name = directory_name + ".zip"
    with zipfile.ZipFile(zip_file_name, "w") as zipf:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                zipf.write(
                    os.path.join(root, file),
                    os.path.relpath(os.path.join(root, file), directory_path),
                )

    return zip_file_name

def read_file_contents(file_name):
    try:
        with open(file_name, 'r') as file:
            file_contents = file.read()
            return file_contents
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    if len(sys.argv) != 2:
        print("Error: Enter directory name where main_prompt file is present")
        return

    file_name = sys.argv[1]+'/main_prompt'

    # Read file contents
    user_project_description = ''
    contents = read_file_contents(file_name)
    if contents is not None:
        user_project_description = contents

    all_quesions = get_all_quesetions(user_project_description) 
    
    qus_list=extract_question_list(all_quesions)
    ques_answer=""
    previous_questions_and_answers=""
    while(len(qus_list)>0):
        print('\nAnything unclear?')
        print("Important areas that need clarification:\n")
        for q in qus_list:
            print(q)
        print("\nClarifying question:")
        qus = qus_list[0]
        ans=input('\n'+qus+"\n(answer in text or enter 'q' (to skip this question) or 'exit' (to skip all the questions).\nYour Ans: ")

        if ans=='exit':
            for q in qus_list:
                previous_questions_and_answers+=q+'\n'
                previous_questions_and_answers+='Answer: Do whatever you think is the best.\n\n'
            break
        else:      
            previous_questions_and_answers+=qus+'\n'
            if ans=='q':
                ans = "Do whatever you think is the best."
            previous_questions_and_answers+='Answer: '+ans+'.\n\n'
            number_match = re.match(r'^(\d+)\.', qus)

            # Extract the number
            if number_match:
                number = number_match.group(1)
                ques_answer+=', '+number

        new_qus = get_project_qus(user_project_description,previous_questions_and_answers, ques_answer)
        qus_list=extract_question_list(new_qus)
    

    project_structure = get_project_structure(user_project_description, previous_questions_and_answers)
    print("Generated project structure:\n", project_structure)
    file_list = extract_file_list(project_structure)
    print("\nList of files to be created: ")
    for id in range(len(file_list)):
        print(str(id)+'. '+file_list[id])

    directory_name = sys.argv[1]+'/workspace'
    zip_file_name = create_directory_and_files(
        directory_name, file_list, user_project_description, project_structure, previous_questions_and_answers
    )
    print("Directory created, files written, and zipped as:", zip_file_name)


if __name__ == "__main__":
    main()
