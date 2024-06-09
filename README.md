# ai-code-genertion-with-gemini-api

This project generates the code for a project by using the Gemini API based on a provided project description.

## Project Structure

The project consists of the following files:

```
.
├── main.py
├── requirements.txt
└── .env
```

## Local Setup

To set up the project locally, follow these steps:

### 1. Install Dependencies

Ensure you have Python installed. To install the required dependencies, run the following command:

```sh
pip install -r requirements.txt
```

### 2. Create .env File

The `.env` file stores environment variables needed for the project. To create it:

1. In the root directory of your project, create a file named `.env`.
2. Open the `.env` file in a text editor and add the following line, replacing `your_gemini_api_key` with your actual Gemini API key:

   ```plaintext
   GEMINI_API_KEY=your_gemini_api_key
   ```

### 3. Prepare Project Directory

You need to create a directory for your project description and a file within it named `main_prompt` that will contain the description.

#### Steps:

1. Create a new directory (e.g., `project_dir_name`):

   ```sh
   mkdir project_dir_name
   ```

2. Navigate into the newly created directory:

   ```sh
   cd project_dir_name
   ```

3. Create a file named `main_prompt` in this directory:

   ```sh
   touch main_prompt
   ```

4. Open the `main_prompt` file in a text editor and write your project description in it. Save and close the file when done.

### 4. Run the Program

With the setup complete, you can now run the program to generate the project code.

#### Steps:

1. Navigate back to the root directory of the project:

   ```sh
   cd ..
   ```

2. Execute the following command, replacing `project_dir_name` with the name of the directory you created:

   ```sh
   python main.py project_dir_name
   ```

### Explanation of Program Execution

When you run the command, the program performs the following steps:

1. **Reads Project Description**: The program reads the project description written in the `main_prompt` file located in `project_dir_name`.
2. **Clarification Questions**: It may ask you some clarification questions to better understand the project requirements.
3. **Generates Code**: The program generates the entire codebase for the project.
4. **Stores Code**: The generated code is stored in a subdirectory named `workspace` within `project_dir_name`.
5. **Creates Zip File**: A zip file of the generated code named `workspace.zip` is created in the same directory.

### Example

Here's a step-by-step example to illustrate the setup and execution:

1. **Create Project Directory**:

   ```sh
   mkdir my_project
   cd my_project
   touch main_prompt
   ```

2. **Write Project Description**:

   Open `main_prompt` in a text editor and add your project description, then save and close the file.

3. **Navigate Back and Run the Program**:

   ```sh
   cd ..
   python main.py my_project
   ```

After running the program, you will find the generated code in `my_project/workspace` and a zipped version in `my_project/workspace.zip`.

## Screen Recording

To further assist you, here’s a screen recording demonstrating how to use this project after doing local setup:

![Screen Recording](https://drive.google.com/file/d/1-PZVWDfB23e_OkMN4VnzvIZyFZtgPjPi/view?usp=sharing)
