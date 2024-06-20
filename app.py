# Add Message model
class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    recipient_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    timestamp = Column(Date, default=date.today)
    text = Column(Text, nullable=False)
    voice_memo = Column(String, nullable=True)
    video = Column(String, nullable=True)
    picture = Column(String, nullable=True)

Base.metadata.create_all(engine)
# Send a message
def send_message(sender_id, recipient_username, text, voice_memo=None, video=None, picture=None):
    recipient = session.query(User).filter_by(username=recipient_username).first()
    if recipient:
        message = Message(sender_id=sender_id, recipient_id=recipient.id, text=text,
                          voice_memo=voice_memo, video=video, picture=picture)
        session.add(message)
        session.commit()
        return True
    return False

# Get messages for a user
def get_messages(user_id):
    sent_messages = session.query(Message).filter_by(sender_id=user_id).all()
    received_messages = session.query(Message).filter_by(recipient_id=user_id).all()
    return sent_messages, received_messages
def main():
    st.title("Private Social Media Platform")

    # Authentication
    if 'user' not in st.session_state:
        st.session_state.user = None

    if st.session_state.user:
        st.sidebar.write(f"Logged in as {st.session_state.user.username}")
        if st.sidebar.button("Logout"):
            st.session_state.user = None

    else:
        st.sidebar.title("Login/Signup")
        login_form = st.sidebar.form(key='login_form')
        username = login_form.text_input("Username")
        password = login_form.text_input("Password", type="password")
        login_btn = login_form.form_submit_button("Login")
        signup_btn = login_form.form_submit_button("Signup")

        if login_btn:
            user = login(username, password)
            if user:
                st.session_state.user = user
                st.sidebar.success("Logged in successfully")
            else:
                st.sidebar.error("Invalid credentials")

        if signup_btn:
            if session.query(User).filter_by(username=username).first():
                st.sidebar.error("Username already taken")
            else:
                signup(username, password)
                st.sidebar.success("Signup successful. Please login.")

    # Emotion Check-In
    if st.session_state.user:
        st.header("Emotion Check-In")
        with st.form(key='emotion_form'):
            emotion = st.text_input("How are you feeling today?")
            note = st.text_area("Any notes?")
            submit_button = st.form_submit_button("Log Emotion")

            if submit_button:
                new_log = EmotionLog(user_id=st.session_state.user.id, emotion=emotion, note=note)
                session.add(new_log)
                session.commit()
                st.success("Emotion logged successfully")

        # Display emotion logs
        st.header("Emotion History")
        logs = session.query(EmotionLog).filter_by(user_id=st.session_state.user.id).all()
        for log in logs:
            st.write(f"{log.date}: {log.emotion} - {log.note}")

        # Messaging Interface
        st.header("Messaging")
        with st.form(key='message_form'):
            recipient = st.text_input("Recipient Username")
            text = st.text_area("Message")
            submit_button = st.form_submit_button("Send Message")

            if submit_button:
                if send_message(st.session_state.user.id, recipient, text):
                    st.success("Message sent successfully")
                else:
                    st.error("Failed to send message. Check the recipient username.")

        # Display messages
        st.header("Your Messages")
        sent_messages, received_messages = get_messages(st.session_state.user.id)

        st.subheader("Sent Messages")
        for msg in sent_messages:
            recipient = session.query(User).filter_by(id=msg.recipient_id).first()
            st.write(f"To {recipient.username} on {msg.timestamp}: {msg.text}")

        st.subheader("Received Messages")
        for msg in received_messages:
            sender = session.query(User).filter_by(id=msg.sender_id).first()
            st.write(f"From {sender.username} on {msg.timestamp}: {msg.text}")

if __name__ == "__main__":
    main()
