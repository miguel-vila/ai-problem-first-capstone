I want to create a python project using FastAPI that can be deployed to Railway.
Let's use uv for dependency management.
The purpose of the project is to create an investor assistant web application, powered by AI.
For now, I don't want you to implement any AI functionality, just the scaffolding of the project.
I want to be able to run it locally, iterate over it, and deploy it to Railway later.

The project is a web app with a frontend where the user has a simple form where they need to input the following fields:

- Ticker Symbol
- Risk Appetite (Low, Medium, High)
- Investment Experience (Beginner, Intermediate, Expert)
- Time Horizon (Short-term, Medium-term, Long-term)

This information is sent to the backend via a POST request to an endpoint /generate-strategy

The output should be:

- Suggested action: Buy/Not Buy
- Reasoning behind the action

Some dependencies I want to use are:

"ipykernel>=7.0.1",
"jupyter>=1.1.1",
"langchain-community==0.3.25",
"langchain-core==0.3.79",
"langchain-openai==0.3.18",
"langchain-tavily==0.2.12",
"langchain[openai]==0.3.25",
"langgraph==0.4.5",
"langgraph-prebuilt==0.2.2",
"opik==1.8.74",
"python-dotenv==1.1.0",

add any other dependencies you think are necessary for this kind of project.

The frontend should be very simple, select a simple and modern tech stack for it.

Output a file named `claude-decisions.md` that contains tech choices that you
are making that are not explicitly mentioned in the prompt. Explain why you are making those choices.
