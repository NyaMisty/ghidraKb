def getAllKeyOpt():
     tool = state.getTool()
     actions = tool.getAllActions()
     ret = []
     for action in actions:
         ret.append('%s (%s)' % (action.getName(), action.getOwner()))
     return ret

import json
print json.dumps(getAllKeyOpt())
