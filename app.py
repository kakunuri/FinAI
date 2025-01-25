import streamlit as st
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools
from phi.storage.agent.sqlite import SqlAgentStorage
from dotenv import load_dotenv
import os


# Set environment variables
os.environ["GROQ_API_KEY"] = "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"
os.environ["OPENAI_API_KEY"] = "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"


# Page config
st.set_page_config(
    page_title="AI Agent Playground",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = "Web Agent"

# Define the agents
web_agent = Agent(
    name="Web Agent",
    model=Groq(id="llama-3.1-8b-instant"),
    tools=[DuckDuckGo()],
    instructions=["Always include sources"],
    storage=SqlAgentStorage(table_name="web_agent", db_file="agents.db"),
    add_history_to_messages=True,
    markdown=True,
)

finance_agent = Agent(
    name="Finance Agent",
    model=Groq(id="llama-3.1-8b-instant"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True, company_news=True,income_statements=True,stock_fundamentals=True,key_financial_ratios=True)],
    instructions=["Use tables to display data"],
    storage=SqlAgentStorage(table_name="finance_agent", db_file="agents.db"),
    add_history_to_messages=True,
    markdown=True,
)

def get_agent():
    return web_agent if st.session_state.selected_agent == "Web Agent" else finance_agent

def main():
    st.title("🤖 AI Agent Playground")
    
    # Sidebar
    with st.sidebar:
        st.header("Settings")
        st.session_state.selected_agent = st.radio(
            "Select Agent",
            ["Web Agent", "Finance Agent"]
        )
        if st.button("Clear Chat"):
            st.session_state.messages = []
    
    # Main chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # User input
    if prompt := st.chat_input(f"Ask the {st.session_state.selected_agent} a question..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    agent = get_agent()
                    response = agent.run(prompt)
                    
                    # Extract just the content from the RunResponse object
                    response_content = response.content
                    
                    # Display the response
                    st.markdown(response_content)
                    
                    # Store the message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_content
                    })
                    
                    # Optional: Display metrics in the sidebar
                    with st.sidebar:
                        with st.expander("Last Response Metrics"):
                            st.write(dict(response.metrics))
                            
                except Exception as e:
                    st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()