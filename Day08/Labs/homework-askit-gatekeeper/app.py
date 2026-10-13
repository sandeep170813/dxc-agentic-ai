import streamlit as st

from gatekeeper import needs_approval, route, safe_to_remember


st.set_page_config(page_title="AskIT Gatekeeper", page_icon="🛡️", layout="centered")

st.title("AskIT Gatekeeper")
st.write("Test the routing, approval, and memory-safety rules from gatekeeper.py.")

text = st.text_area("Text", placeholder="Enter a ticket, action note, or fact to evaluate.")
action = st.selectbox(
    "Action",
    ["search_kb", "get_ticket", "reset_password", "update_ticket", "grant_access"],
)
user_id = st.text_input("User ID", value="EMP-1002")
hour = st.number_input("Hour", min_value=0, max_value=23, value=10, step=1)

col1, col2, col3 = st.columns(3)


def show_result(label: str, value) -> None:
    st.subheader(label)
    st.json(value)


with col1:
    if st.button("Route"):
        try:
            show_result("route", {"team": route(text)})
        except Exception as exc:
            st.error(str(exc))

with col2:
    if st.button("Needs approval"):
        try:
            show_result(
                "needs_approval",
                needs_approval(action, user_id, int(hour)),
            )
        except Exception as exc:
            st.error(str(exc))

with col3:
    if st.button("Safe to remember"):
        try:
            show_result("safe_to_remember", {"safe": safe_to_remember(text)})
        except Exception as exc:
            st.error(str(exc))