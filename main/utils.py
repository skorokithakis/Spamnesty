import random
import re


def parse_email_address(address: str):
    """
    Break an email address of the form First Last <firstlast@example.com> into
    a name and an email address.
    """
    regexes = [
        # Bare email addresses (per@ex.com)
        "^()([^<>]*)$",
        # Weird-ass Outlook format (Person <per@ex.com<mailto:per@ex.com>>).
        "^\s*\"?(.*?)\"?\s*<(.*?)<.*?>>$",
        # Regular format (Person <per@ex.com>).
        "^\s*\"?(.*?)\"?\s*<(.*?)>\s*$",
    ]
    # Try each regex in order, to find one that matches.
    for regex in regexes:
        match = re.match(regex, address)
        if not match:
            continue
        return match.groups()

    raise ValueError("Could not parse input: %s" % address)


def normalize_email_address(address: str):
    """
    Normalize an email address to either a "First Last <flast@ex.com>" or a
    "flast@ex.com" format.
    """
    display_name, email = parse_email_address(address)
    if display_name:
        return "%s <%s>" % (display_name, email)
    else:
        return email


def parse_forwarded_message(message: str):
    """
    Parse an email body that contains a forwarded message, and return the
    message and the original sender's email address.
    """
    state = "START"
    sender = None
    body = []
    regex = re.compile(
        r"""
        [\r\n][\t\f\v ]*    # Ignore any whitespace before the header.
        (Reply-To|From):    # Match the header.
        \s*                 # Ignore whitespace after it.
        ((?:.*?)            # Non-preserving group of anything before the @.
        @                   # The actual "@" sign (it all hinges on this, so if
                            # some madman has a quoted "@" in their email address,
                            # we're out of luck.
        (?:[^\r\n]*))       # Match anything remaining, up to a newline.
        """,
        re.DOTALL | re.IGNORECASE | re.VERBOSE
    )

    # Match headers, but only keep the first two matches. If there are more,
    # there is either some junk before or after the header. In the former case,
    # the message is junk because the forwarder added it, in the latter, we only
    # need the first two anyway.
    matches = regex.findall(message)[:2]
    if not matches:
        # No sender found.
        return sender, ""
    elif len(matches) > 1 and matches[1][0].lower() == "reply-to":
        # If the second address is a Reply-To, keep it.
        sender = matches[1][1]
    else:
        # Otherwise, keep the first address.
        sender = matches[0][1]

    sender = normalize_email_address(sender)

    # Parse the header so we can recover the original message.
    for line in message.split("\n"):
        line = line.strip("\r\n")
        if state == "START":
            match = re.match("^From:.*$", line)
            if match:
                state = "HEADER"
        elif state == "EMAIL":
            pass
        elif state == "HEADER":
            # Start reading the message on the first blank line.
            if line == "":
                state = "MESSAGE"
        else:
            body.append(line)

    return sender, "\n".join(body).lstrip()


def quote_message(body: str, message):
    """
    Given a body and an EmailMessage instance, construct a body (with a
    signature) and a quoted reply.
    """

    original = body.split("\n")
    original.append("")
    original.append(message.conversation.sender_name)
    original.append("CEO, %s" % message.conversation.domain.company_name)

    reply = []
    reply.append("On %s, %s wrote:" % (message.timestamp.strftime("%d/%m/%Y %H:%M %p"), message.sender_name))
    reply.extend(["> " + line for line in message.best_body.split("\n")])
    return "\n".join(original), "\n".join(reply)


def get_random_message():
    messages = [
        "Hello,\nThat is very interesting! Could you elaborate? Do you have any details online I could look at?",
        "Hi,\nSounds great, how can we proceed? We're interested in getting started pretty much immediately, as we could use this.",
        "Hello,\nThank you for your email! However, I don't know if this will fit in our budget. Is there anything better you could do?",
        "Hey there,\nCould you tell me where you are located? Also, could you tell me more about your offer?",
        "Hello,\nThat is reasonable, but do you think you can go into more detail about your main product? What is it about, exactly?",
        "Hello,\nThat is very helpful, thank you. Do you perhaps have some literature I could look at, or could you send me some more information about what exactly makes you unique?",
        "Hi,\nGreat, thanks. Could we have a short call to discuss the specifics? What are your contact details? Also, what is your pricing model like?",
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

    original, reply = quote_message(get_random_message(), message)

    reply = Message.objects.create(
        direction="S",
        conversation=message.conversation,
        sender=message.conversation.sender_email,
        recipient=message.sender,
        subject=subject,
        body=original,
        quoted_text=reply,
        in_reply_to=message.message_id,
    )
    return reply
