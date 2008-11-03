name = "DBUS Caller"
section = "DBUSCaller"

def description(event):
    result = u"Call " + event['interface'] + u"." + event['method'] + u"("
    if 'arguments' in event:
    	result += ", ".join(unicode(arg) for arg in event['arguments'])
    result += u") on " + event['service'] + event['object']
    return result