name = "Keyboard/Mouse (Kernel)"
section = "UinputDispatcher"

# TODO: Create description function for UinputDispatcher
def description(event):
    result = ""
    if event['type'] == "key":
        result += u"Keypress: %s" % unicode(event['map_to'])
    elif event['type'] == "mousebutton":
        result += u"Mousebutton: %s" % unicode(event['map_to'])
    elif event['type'] == "mousewheel":
        result += u"Mousewheel: %s" % unicode(event['map_to'])
    elif event['type'] == "mouseaxis":
        result += u"Mouseaxis direction: %s" % event['map_to']
    if "repeat_freq" in event:
        result += " "
        result += "(Repeat: %s/s)" % str(event['repeat_freq'])
    return result