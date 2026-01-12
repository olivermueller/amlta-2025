"""
Chatbot Arena - Human Evaluation Interface

A Gradio app for comparing two LLM responses side-by-side.
Users can vote for the better response (A or B) or declare a tie.
Results are stored in a SQLite database.
Models are randomly assigned and hidden from the user.
"""
import os
import gradio as gr
import sqlite3
import random
from datetime import datetime
from langchain_openai import ChatOpenAI

# Available models for comparison
MODELS = [
    "llama3.2:1b",
    "qwen3:0.6b",
    "gemma3:270m",
    "llama3.2:3b",
    "qwen3:1.7b"
]

# SQLite database file
DB_FILE = "evaluation_results.db"

if not os.path.exists(DB_FILE):
    open(DB_FILE, 'w').close()


def init_db():
    """Initialize the SQLite database and create table if not exists."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            prompt TEXT,
            chatbot_a TEXT,
            chatbot_a_answer TEXT,
            chatbot_b TEXT,
            chatbot_b_answer TEXT,
            win TEXT
        )
    """)
    conn.commit()
    conn.close()


def load_results():
    """Load all results from database."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM evaluations")
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "id": row[0],
            "timestamp": row[1],
            "prompt": row[2],
            "chatbot_a": row[3],
            "chatbot_a_answer": row[4],
            "chatbot_b": row[5],
            "chatbot_b_answer": row[6],
            "win": row[7]
        })
    return results


def save_result(prompt, response_a, response_b, model_a, model_b, winner_name):
    """Save a single evaluation result to SQLite database."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO evaluations (timestamp, prompt, chatbot_a, chatbot_a_answer, chatbot_b, chatbot_b_answer, win)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        prompt,
        model_a,
        response_a,
        model_b,
        response_b,
        winner_name
    ))
    conn.commit()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM evaluations")
    total = cursor.fetchone()[0]
    conn.close()
    return total


def get_response(prompt: str, model: str) -> str:
    """Get a response from the specified model using LangChain."""
    try:
        llm = ChatOpenAI(
            model=model,
            api_key="ollama",
            base_url="http://localhost:11434/v1",
            temperature=0.7,
            max_tokens=1024
        )
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error: {str(e)}"


def generate_responses(prompt: str):
    """Generate responses from two randomly selected models."""
    if not prompt.strip():
        return (
            gr.update(value=[]),
            gr.update(value=[]),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            "",
            "",
            "",
            "",
            ""
        )
    
    # Randomly select two different models
    selected_models = random.sample(MODELS, 2)
    model_a = selected_models[0]
    model_b = selected_models[1]
    
    response_a = get_response(prompt, model_a)
    response_b = get_response(prompt, model_b)
    
    # Create chat history format for the new Gradio chatbot
    history_a = [{"role": "user", "content": prompt}, {"role": "assistant", "content": response_a}]
    history_b = [{"role": "user", "content": prompt}, {"role": "assistant", "content": response_b}]
    
    return (
        gr.update(value=history_a),
        gr.update(value=history_b),
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=False),
        prompt,
        response_a,
        response_b,
        model_a,
        model_b
    )


def vote(choice: str, prompt: str, response_a: str, response_b: str, model_a: str, model_b: str):
    """Record a vote for the preferred response."""
    if not prompt:
        return "No responses to vote on yet!", [], [], "", gr.update(visible=False), gr.update(visible=False), "No evaluations recorded yet."
    
    # Determine the winning chatbot name
    if choice == "A":
        winner_name = model_a
        winner_text = f"✅ You voted for **Model A** (was: {model_a})"
    else:
        winner_name = model_b
        winner_text = f"✅ You voted for **Model B** (was: {model_b})"
    
    total = save_result(prompt, response_a, response_b, model_a, model_b, winner_name)
    
    # Reveal the models after voting
    reveal_text = f"🔍 **Models revealed:**\n- Model A: `{model_a}`\n- Model B: `{model_b}`"
    
    result = f"{winner_text}\n\n{reveal_text}\n\n📊 Total evaluations recorded: {total}"
    
    # Get updated statistics
    updated_stats = get_statistics()
    
    # Return result text, cleared chatbots, cleared prompt, hidden buttons, updated stats
    return result, [], [], "", gr.update(visible=False), gr.update(visible=False), updated_stats


def get_statistics():
    """Get current evaluation statistics."""
    results = load_results()
    if not results:
        return "No evaluations recorded yet."
    
    total = len(results)
    
    model_wins = {}
    for r in results:
        winner = r.get("win", "")
        if winner:
            model_wins[winner] = model_wins.get(winner, 0) + 1
    
    stats_text = f"""## 📊 Evaluation Statistics

**Total Evaluations:** {total}

### Model Win Counts:
"""
    for model, wins in sorted(model_wins.items(), key=lambda x: -x[1]):
        win_rate = 100 * wins / total
        stats_text += f"- **{model}**: {wins} wins ({win_rate:.1f}%)\n"
    
    return stats_text


# Build the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("""
    # 🏟️ Chatbot Arena
    
    Compare responses from different LLMs side-by-side and vote for the better one!
    
    Two random models are selected for each prompt. You won't know which model is which until after voting!
    
    1. **Enter your prompt** below (press **Cmd+Enter** to generate)
    2. **Vote** for the better response
    3. The models will be **revealed** after your vote
    """)
    
    # State variables
    current_prompt = gr.State("")
    current_response_a = gr.State("")
    current_response_b = gr.State("")
    current_model_a = gr.State("")
    current_model_b = gr.State("")
    
    # Chatbots first (above prompt)
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 🅰️ Model A (hidden)")
            chatbot_a = gr.Chatbot(
                label="Model A Response",
                height=400
            )
        with gr.Column():
            gr.Markdown("### 🅱️ Model B (hidden)")
            chatbot_b = gr.Chatbot(
                label="Model B Response",
                height=400
            )
    
    gr.Markdown("### 🗳️ Vote for the Better Response")
    
    with gr.Row():
        vote_a_btn = gr.Button("👈 A is better", variant="secondary", visible=False)
        vote_b_btn = gr.Button("👉 B is better", variant="secondary", visible=False)
    
    result_text = gr.Markdown(visible=False)
    
    # Prompt input below responses
    prompt_input = gr.Textbox(
        label="Your Prompt",
        placeholder="Enter your prompt here... (Cmd+Enter to generate)",
        lines=3
    )
    
    generate_btn = gr.Button("🚀 Generate Responses", variant="primary", size="lg")
    
    with gr.Accordion("📊 View Statistics", open=False):
        stats_btn = gr.Button("Refresh Statistics")
        stats_output = gr.Markdown()
    
    # Event handlers
    generate_btn.click(
        fn=generate_responses,
        inputs=[prompt_input],
        outputs=[
            chatbot_a, 
            chatbot_b, 
            vote_a_btn, 
            vote_b_btn,
            result_text,
            current_prompt,
            current_response_a,
            current_response_b,
            current_model_a,
            current_model_b
        ]
    )
    
    # Cmd+Enter to generate
    prompt_input.submit(
        fn=generate_responses,
        inputs=[prompt_input],
        outputs=[
            chatbot_a, 
            chatbot_b, 
            vote_a_btn, 
            vote_b_btn,
            result_text,
            current_prompt,
            current_response_a,
            current_response_b,
            current_model_a,
            current_model_b
        ]
    )
    
    vote_a_btn.click(
        fn=lambda p, ra, rb, ma, mb: vote("A", p, ra, rb, ma, mb),
        inputs=[current_prompt, current_response_a, current_response_b, current_model_a, current_model_b],
        outputs=[result_text, chatbot_a, chatbot_b, prompt_input, vote_a_btn, vote_b_btn, stats_output]
    ).then(
        fn=lambda: gr.update(visible=True),
        outputs=[result_text]
    )
    
    vote_b_btn.click(
        fn=lambda p, ra, rb, ma, mb: vote("B", p, ra, rb, ma, mb),
        inputs=[current_prompt, current_response_a, current_response_b, current_model_a, current_model_b],
        outputs=[result_text, chatbot_a, chatbot_b, prompt_input, vote_a_btn, vote_b_btn, stats_output]
    ).then(
        fn=lambda: gr.update(visible=True),
        outputs=[result_text]
    )
    
    stats_btn.click(
        fn=get_statistics,
        outputs=[stats_output]
    )


if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
