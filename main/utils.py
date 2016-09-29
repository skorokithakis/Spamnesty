import random
import re


def parse_forwarded_message(message: str):
    """
    Parse an email body that contains a forwarded message, and return the
    message and the original sender's email address.
    """
    state = "START"
    sender = None
    body = []
    for line in message.split("\n"):
        line = line.strip("\r\n")
        if state == "START":
            match = re.match("From:\W*(.*?)$", line)
            if match:
                state = "HEADER"
                sender = match.group(1).strip()
        elif state == "HEADER":
            # Start reading the message on the first blank line.
            if line == "":
                state = "MESSAGE"
        else:
            body.append(line)

    return sender, "\n".join(body).lstrip()


def quote_message(body: str, message):
    """
    Given a body and an EmailMessage instance, construct a reply that contains
    the body and quoted EmailMessage contents.
    """

    lines = body.split("\n")
    lines.append("")
    lines.append(message.conversation.sender_name)
    lines.append("CEO, %s" % message.conversation.domain.company_name)
    lines.extend(["", ""])
    lines.append("On %s, %s wrote:" % (message.timestamp.strftime("%d/%m/%Y %H:%M %p"), message.sender_name))

    original = message.stripped_body or message.body
    lines.extend(["> " + line for line in original.split("\n")])
    return "\n".join(lines)


def get_random_message():
    messages = [
        "Hello,\nThat is very interesting! Could you elaborate? Do you have any details online I could look at?",
        "Hi,\nSounds great, how can we proceed? We're interested in getting started pretty much immediately, as we could use this.",
        "Hello,\nThank you for your email! However, I don't know if this will fit in our budget. Is there anything better you could do?",
        "Hey there,\nCould you tell me where you are located? Also, could you tell me more about your offer?",
    ]
    return random.choice(messages)


def construct_reply(message):
    """
    Construct a reply to the received message.
    """
    subject = message.subject
    if not subject.startswith("Re: "):
        subject = "Re: " + subject

    # We can't import a model here, as it would be circular.
    Message = message.__class__

    reply = Message.objects.create(
        direction="S",
        conversation=message.conversation,
        sender=message.conversation.sender_email,
        recipient=message.sender,
        subject=subject,
        body=quote_message(get_random_message(), message),
        in_reply_to=message.message_id,
    )
    return reply
