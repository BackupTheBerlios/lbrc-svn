name = "Command Executor"
section = "CommandExecutor"

def description(event):
    result = unicode(event['command'])
    if 'arguments' in event:
        for arg in event['arguments']:
            result += u" '" + unicode(arg) + u"'"
    return result