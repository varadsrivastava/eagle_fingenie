
msg = {"content": "Thank you. I'll transfer this information to my relationship manager. Thank you for your information."}

def is_termination_msg(msg):
    print("relationship manager" in msg["content"].lower())

is_termination_msg(msg)