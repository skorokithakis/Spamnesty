import random


from .models import Message


def quote_message(reply, message):
    body = ("%s\n\n%s" % (message.stripped_body, message.stripped_signature)) if message.stripped_body else message.body

    lines = reply.split("\n")
    lines.append("")
    lines.append(message.conversation.sender_name)
    lines.append("CEO, MNesty, LLC")
    lines.extend(["", ""])
    lines.append("On %s, %s wrote:" % (message.timestamp.strftime("%d/%m/%Y %H:%M %p"), message.sender_name))
    lines.extend(["> " + line for line in body.split("\n")])
    return "\n".join(lines)


def get_random_message():
    messages = [
        "Hello,\nThat is very interesting! Could you elaborate? Do you have any details\nonline I could look at?",
        "Hi,\nSounds great, how can we proceed? We're interested in getting started\npretty much immediately, as we could use this.",
        "Hello,\nThank you for your email! However, I don't know if this will fit in\nour budget. Is there anything better you could do?",
        "Hey there,\nCould you tell me where you are located? Also, could you tell me\nmore about your offer?",
    ]
    return random.choice(messages)


def construct_reply(message):
    """
    Construct a reply to the received message.
    """
    subject = message.subject
    if not subject.startswith("Re: "):
        subject = "Re: " + subject

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
