import base64
import html
from datetime import datetime
from pathlib import Path

import streamlit as st

import command_router
from command_router import route_command
from gpt_brain import interpret_with_gpt, generate_chat_summary
from memory_manager import save_chat_summary
from utils.voice_io import listen as voice_listen
from utils.voice_io import speak as voice_speak


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Assistant",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# PATHS / 3 ASSISTANT IMAGES ONLY
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "assistant_assets"

ASSISTANT_IMAGES = {
    "idle": ASSET_DIR / "idle.png",
    "thinking": ASSET_DIR / "thinking.png",
    "speaking": ASSET_DIR / "speaking.png",
}


# =========================================================
# SESSION STATE
# =========================================================

def initialize_state():
    defaults = {
        "assistant_state": "idle",
        "current_command": "Waiting for your command...",
        "response": "Hello! I am your assistant.",
        "status": "Ready",
        "messages": [],
        "conversation_history": [],
        "session_summary_saved": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_state()


# =========================================================
# STYLING
# =========================================================

st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at 36% 28%, rgba(66, 71, 185, 0.13), transparent 30%),
                linear-gradient(180deg, #070b12 0%, #090d16 100%);
            color: #f7f8fc;
        }

        .block-container {
            max-width: 1550px;
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        .assistant-shell {
            min-height: 92vh;
            border: 1px solid rgba(133, 143, 181, 0.20);
            border-radius: 24px;
            background: rgba(8, 13, 24, 0.80);
            padding: 28px 32px;
            box-shadow: inset 0 0 60px rgba(55, 64, 150, 0.05);
        }

        .brand-row {
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 22px;
        }

        .brand-icon {
            width: 45px;
            height: 45px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 25px;
            color: #b5b9ff;
            background: rgba(77, 67, 185, 0.20);
            box-shadow: 0 0 24px rgba(80, 80, 255, 0.25);
        }

        .brand-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #f4f5fb;
            line-height: 1.15;
        }

        .brand-subtitle {
            color: #999fe9;
            margin-top: 5px;
            font-size: 0.92rem;
        }

        .assistant-image-wrap {
            min-height: 390px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 10px 0 4px 0;
        }

        .assistant-image {
            max-width: 430px;
            width: min(65%, 430px);
            filter: drop-shadow(0 0 30px rgba(86, 91, 255, 0.28));
        }

        .assistant-image-fallback {
            width: 260px;
            height: 260px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 50px auto;
            font-size: 84px;
            background: radial-gradient(circle, rgba(74, 78, 183, .34), rgba(10, 14, 28, .92));
            border: 2px solid rgba(113, 121, 255, .50);
            box-shadow: 0 0 50px rgba(73, 77, 255, .22);
        }

        .assistant-response {
            text-align: center;
            font-size: 1.65rem;
            font-weight: 600;
            margin-top: 8px;
            color: #f4f5fa;
        }

        .assistant-status {
            text-align: center;
            font-size: 1rem;
            color: #9299b8;
            margin-top: 10px;
            margin-bottom: 28px;
        }

        .command-card {
            max-width: 650px;
            margin: 0 auto 18px auto;
            border: 1px solid rgba(121, 130, 181, 0.18);
            border-radius: 22px;
            background: rgba(16, 23, 38, 0.78);
            padding: 22px 26px;
            text-align: center;
        }

        .command-label {
            color: #aaa6fa;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .command-text {
            color: #7f98ff;
            font-size: 1.35rem;
            font-weight: 600;
            margin-top: 8px;
            word-break: break-word;
        }

        .chat-shell {
            border: 1px solid rgba(133, 143, 181, 0.20);
            border-radius: 24px;
            background: rgba(11, 16, 27, 0.90);
            padding: 24px 20px 12px 20px;
            min-height: 84vh;
        }

        .chat-title {
            color: #f3f4f8;
            font-size: 1.25rem;
            font-weight: 700;
            margin: 2px 5px 16px 5px;
        }

        .chat-divider {
            display: flex;
            align-items: center;
            gap: 12px;
            color: #9c9adf;
            font-size: 0.78rem;
            margin: 10px 0 18px 0;
        }

        .chat-divider::before,
        .chat-divider::after {
            content: "";
            height: 1px;
            background: rgba(118, 126, 162, 0.14);
            flex: 1;
        }

        .chat-scroll {
            max-height: 68vh;
            overflow-y: auto;
            padding: 2px 6px 12px 6px;
            scrollbar-width: thin;
        }

        .message-row {
            display: flex;
            margin-bottom: 14px;
        }

        .message-row.user {
            justify-content: flex-end;
        }

        .message-row.assistant {
            justify-content: flex-start;
        }

        .bubble {
            max-width: 88%;
            border-radius: 17px;
            padding: 12px 14px 9px 14px;
            line-height: 1.45;
            font-size: 0.92rem;
            word-break: break-word;
            white-space: pre-wrap;
        }

        .bubble.user {
            background: linear-gradient(135deg, rgba(54, 54, 154, .94), rgba(74, 52, 173, .94));
            color: #f8f8ff;
            border-bottom-right-radius: 5px;
        }

        .bubble.assistant {
            background: rgba(27, 34, 47, 0.96);
            color: #f0f2f6;
            border: 1px solid rgba(126, 138, 175, 0.09);
            border-bottom-left-radius: 5px;
        }

        .time {
            font-size: 0.70rem;
            color: #a0a5bd;
            margin-top: 7px;
            text-align: right;
        }

        .empty-chat {
            color: #80869e;
            text-align: center;
            padding: 70px 12px;
            line-height: 1.6;
        }

        div.stButton > button {
            border-radius: 16px;
            min-height: 48px;
            border: 1px solid rgba(122, 130, 255, 0.38);
            background: rgba(28, 34, 57, 0.88);
            color: #f4f4fb;
            font-weight: 600;
        }

        div.stButton > button:hover {
            border-color: rgba(135, 123, 255, 0.78);
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HELPERS
# =========================================================

def current_time():
    return datetime.now().strftime("%I:%M %p").lstrip("0")


def add_message(role, message):
    if not message:
        return

    st.session_state.messages.append(
        {
            "role": role,
            "message": str(message),
            "time": current_time(),
        }
    )


def image_data_uri(path):
    if not path.exists():
        return None

    suffix = path.suffix.lower().replace(".", "")
    mime = "jpeg" if suffix in {"jpg", "jpeg"} else suffix

    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:image/{mime};base64,{encoded}"


def build_chat_html():
    parts = [
        '<div class="chat-title">Chat History</div>',
        '<div class="chat-divider">Today</div>',
        '<div class="chat-scroll">',
    ]

    if not st.session_state.messages:
        parts.append(
            '<div class="empty-chat">Your current conversation will appear here.</div>'
        )
    else:
        for item in st.session_state.messages:
            role = "user" if item["role"] == "user" else "assistant"
            message = html.escape(item["message"])
            timestamp = html.escape(item["time"])

            parts.append(
                f'<div class="message-row {role}">'
                f'<div class="bubble {role}">'
                f'{message}'
                f'<div class="time">{timestamp}</div>'
                f'</div>'
                f'</div>'
            )

    parts.append("</div>")
    return "".join(parts)


def render_chat(placeholder):
    placeholder.markdown(
        build_chat_html(),
        unsafe_allow_html=True,
    )


def render_assistant(placeholder):
    state = st.session_state.assistant_state
    image_path = ASSISTANT_IMAGES.get(state, ASSISTANT_IMAGES["idle"])
    image_uri = image_data_uri(image_path)

    if image_uri:
        image_html = (
            '<div class="assistant-image-wrap">'
            f'<img class="assistant-image" src="{image_uri}" alt="Assistant {state}">'
            "</div>"
        )
    else:
        image_html = (
            '<div class="assistant-image-wrap">'
            '<div class="assistant-image-fallback">✦</div>'
            "</div>"
        )

    response = html.escape(st.session_state.response)
    status = html.escape(st.session_state.status)
    command = html.escape(st.session_state.current_command)

    assistant_html = "".join([
        '<div class="assistant-shell">',
        '<div class="brand-row">',
        '<div class="brand-icon">✦</div>',
        '<div>',
        '<div class="brand-title">AI Assistant</div>',
        '<div class="brand-subtitle">Always here. Ready when you are.</div>',
        '</div>',
        '</div>',
        image_html,
        f'<div class="assistant-response">{response}</div>',
        f'<div class="assistant-status">{status}</div>',
        '<div class="command-card">',
        '<div class="command-label">Current Command</div>',
        f'<div class="command-text">{command}</div>',
        '</div>',
        '</div>',
    ])

    placeholder.markdown(
        assistant_html,
        unsafe_allow_html=True,
    )


def set_assistant_state(state, response=None, status=None, command=None):
    st.session_state.assistant_state = state

    if response is not None:
        st.session_state.response = response

    if status is not None:
        st.session_state.status = status

    if command is not None:
        st.session_state.current_command = command

    if LEFT_PLACEHOLDER is not None:
        render_assistant(LEFT_PLACEHOLDER)


# These are assigned after the page columns are created.
LEFT_PLACEHOLDER = None
CHAT_PLACEHOLDER = None


# =========================================================
# STREAMLIT-AWARE VOICE WRAPPERS
# =========================================================

def ui_speak(text):
    """
    Keeps the existing pyttsx3 voice output, while also showing every
    assistant sentence in the Streamlit chat panel.
    """

    text = str(text)

    st.session_state.response = text
    st.session_state.assistant_state = "speaking"
    st.session_state.status = "Speaking..."

    add_message("assistant", text)

    if LEFT_PLACEHOLDER is not None:
        render_assistant(LEFT_PLACEHOLDER)

    if CHAT_PLACEHOLDER is not None:
        render_chat(CHAT_PLACEHOLDER)

    voice_speak(text)


def ui_listen():
    """
    Uses the existing SpeechRecognition microphone function and mirrors
    recognized speech into Streamlit chat.
    """

    set_assistant_state(
        "idle",
        response="I'm listening...",
        status="Listening...",
    )

    command = voice_listen()

    if command:
        command = command.strip()
        st.session_state.current_command = command
        add_message("user", command)

        if CHAT_PLACEHOLDER is not None:
            render_chat(CHAT_PLACEHOLDER)

    return command


# command_router.py imported speak/listen directly, so patch its module-level
# references here. No changes are required in command_router.py or voice_io.py.
command_router.speak = ui_speak
command_router.listen = ui_listen


# =========================================================
# SESSION SUMMARY
# =========================================================

def save_current_session_summary():
    if st.session_state.session_summary_saved:
        return

    history = st.session_state.conversation_history

    if not history:
        return

    try:
        summary = generate_chat_summary(history)

        if summary:
            save_chat_summary(summary)
            st.session_state.session_summary_saved = True

    except Exception as error:
        print("Summary error:", error)


# =========================================================
# MAIN COMMAND FLOW
# =========================================================

def process_voice_command():
    command = ui_listen()

    if not command:
        set_assistant_state(
            "idle",
            response="I didn't catch that. Please try again.",
            status="Ready",
            command="Waiting for your command...",
        )
        return

    lower_command = command.lower().strip()

    # Same exit behavior as assistant.py
    if lower_command == "exit" or lower_command == "stop":
        save_current_session_summary()
        ui_speak("Goodbye!")
        set_assistant_state(
            "idle",
            response="Session ended.",
            status="Ready",
        )
        return

    # Save user message to current-session GPT memory.
    st.session_state.conversation_history.append(
        {
            "role": "user",
            "content": command,
        }
    )

    set_assistant_state(
        "thinking",
        response="Let me check that for you...",
        status="Thinking...",
        command=command,
    )

    try:
        gpt_response = interpret_with_gpt(
            command,
            st.session_state.conversation_history[:-1],
        )

        print("GPT:", gpt_response)

        # Keep the same temporary-memory format used by assistant.py.
        st.session_state.conversation_history.append(
            {
                "role": "assistant",
                "content": gpt_response,
            }
        )

        set_assistant_state(
            "speaking",
            response="Working on it...",
            status="Executing command...",
        )

        # Existing router + existing tools + existing permanent memory.
        route_command(gpt_response)

        set_assistant_state(
            "idle",
            status="Ready",
        )

    except Exception as error:
        print("Assistant error:", error)

        add_message(
            "assistant",
            "I ran into an error while processing that command.",
        )

        if CHAT_PLACEHOLDER is not None:
            render_chat(CHAT_PLACEHOLDER)

        set_assistant_state(
            "idle",
            response="I ran into an error while processing that command.",
            status="Ready",
        )


# =========================================================
# PAGE LAYOUT
# =========================================================

main_col, chat_col = st.columns([3.1, 1.15], gap="medium")

with main_col:
    LEFT_PLACEHOLDER = st.empty()
    render_assistant(LEFT_PLACEHOLDER)

    mic_left, mic_center, mic_right = st.columns([1.4, 1, 1.4])

    with mic_center:
        if st.button(
            "🎙  Listen",
            use_container_width=True,
            type="primary",
        ):
            process_voice_command()

with chat_col:
    with st.container(border=True):
        CHAT_PLACEHOLDER = st.empty()
        render_chat(CHAT_PLACEHOLDER)

        if st.button(
            "Clear Chat History",
            use_container_width=True,
            key="clear_chat_history",
        ):
            st.session_state.messages = []
            render_chat(CHAT_PLACEHOLDER)
