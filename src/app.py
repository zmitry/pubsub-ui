import streamlit as st
from pubsub_client import PubSubClient
from storage import LocalStorage


@st.cache_resource
def get_pubsub_client():
    return PubSubClient()


@st.cache_resource
def get_storage():
    return LocalStorage()


@st.dialog("Create New Topic")
def show_topic_dialog(project_id: str):
    st.subheader("Create New Topic")
    with st.form("create_topic_form"):
        topic_id = st.text_input("Topic Name")
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.form_submit_button("Create"):
                if topic_id:
                    try:
                        topic = st.session_state.pubsub.create_topic(
                            project_id,
                            topic_id
                        )
                        st.success(f"Created topic: {topic}")
                        return True
                    except Exception as e:
                        st.error(f"Error creating topic: {str(e)}")
                        return False
        with col2:
            if st.form_submit_button("Cancel"):
                return False


@st.dialog("Create New Subscription")
def show_subscription_dialog(project_id: str, topic_path: str):
    st.subheader("Create New Subscription")
    with st.form("create_subscription_form"):
        sub_id = st.text_input("Subscription Name")
        col1, col2 = st.columns([1, 4])
        if st.form_submit_button("Create"):
            if sub_id:
                try:
                    sub = st.session_state.pubsub.create_subscription(
                        project_id,
                        sub_id,
                        topic_path
                    )
                    st.success(f"Created subscription: {sub}")
                    return True
                except Exception as e:
                    st.error(f"Error creating subscription: {str(e)}")
                    return False
        if st.form_submit_button("Cancel"):
            return False


def main():
    st.set_page_config(
            page_title="PubSub Emulator UI",
            page_icon="📨",
            layout="wide"
    )
    # Initialize state
    if 'pubsub' not in st.session_state:
        st.session_state.pubsub = get_pubsub_client()
    if 'storage' not in st.session_state:
        st.session_state.storage = get_storage()
    
    # Sidebar
    with st.sidebar:
        # Get saved project ID
        saved_project = st.session_state.storage.get('project_id')
        project_id = st.text_input(
            "Project ID",
            value=saved_project if saved_project else ""
        )
        if project_id:
            # Save project ID if changed
            if (project_id != saved_project or
                    'project_id' not in st.session_state):
                st.session_state.storage.set('project_id', project_id)
                st.session_state.project_id = project_id
            elif 'project_id' not in st.session_state:
                st.session_state.project_id = project_id
            
            # Topic Management in Sidebar
            try:
                client = st.session_state.pubsub
                topics = client.list_topics(st.session_state.project_id)
                if topics:
                    selected_topic = st.selectbox(
                        "Select Topic",
                        topics
                    )
                    if selected_topic:
                        st.session_state.selected_topic = selected_topic
                        st.session_state.subs_list = (
                            st.session_state.pubsub.list_subscriptions(
                                st.session_state.project_id,
                                topic=selected_topic
                            )
                        )
                else:
                    st.info("No topics found")
            except Exception as e:
                st.error(f"Error listing topics: {str(e)}")
            
            if st.button("Create Topic"):
                result = show_topic_dialog(st.session_state.project_id)
                if result:
                    st.rerun()
            if selected_topic:
                try:
                    if st.session_state.subs_list:
                        selected_sub = st.selectbox(
                            "Select Subscription",
                            st.session_state.subs_list
                        )
                        if selected_sub:
                            st.session_state.selected_sub = selected_sub
                    else:
                        st.info("No subscriptions found")
                except Exception as e:
                    st.error(f"Error listing subscriptions: {str(e)}")
                if st.button("Create Subscription"):
                    result = show_subscription_dialog(
                        st.session_state.project_id,
                        st.session_state.selected_topic
                    )
                    if result:
                        st.rerun()
                   
    # Main Content
    st.title("PubSub Emulator UI")
    
    if 'project_id' in st.session_state and 'selected_topic' in st.session_state:
        # Show topic details
        st.json({
            "project_id": st.session_state.project_id,
            "subscription": st.session_state.selected_sub,
            "topic": st.session_state.selected_topic,
        })
        
        # Message Operations
        st.header("Message Operations")
        message = st.text_area("Message Content")
        if st.button("Publish Message"):
            if message:
                try:
                    topic_path = (
                        f"projects/{st.session_state.project_id}"
                        f"/topics/{st.session_state.selected_topic}"
                    )
                    msg_id = st.session_state.pubsub.publish_message(
                        topic_path,
                        message
                    )
                    st.success(f"Published message: {msg_id}")
                except Exception as e:
                    st.error(f"Error publishing message: {str(e)}")
        
        # Pull Messages
        if 'selected_sub' in locals() and selected_sub:
            if st.button("Pull Messages"):
                try:
                    sub_path = (
                        f"projects/{st.session_state.project_id}"
                        f"/subscriptions/{selected_sub}"
                    )
                    messages = st.session_state.pubsub.pull_messages(sub_path)
                    if messages:
                        for msg in messages:
                            msg_id = msg['message_id']
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                with st.expander(f"Message {msg_id}"):
                                    st.json(msg)
                            with col2:
                                if st.button("Ack", key=f"ack_{msg_id}"):
                                    try:
                                        st.session_state.pubsub.ack_message(
                                            sub_path,
                                            msg['ack_id']
                                        )
                                        st.success(f"Acknowledged: {msg_id}")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(
                                            f"Error acknowledging: {str(e)}"
                                        )
                    else:
                        st.info("No messages available")
                except Exception as e:
                    st.error(f"Error pulling messages: {str(e)}")
    else:
        st.info("Please select a project and topic from the sidebar")


if __name__ == "__main__":
    main()
