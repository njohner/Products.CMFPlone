#NOTE: that workflows are 'chains' that can progress from workflow to workflow

from Products.CMFCore.utils import getToolByName

debug = 1

def log(msg):
    import sys
    sys.stdout.write( str(msg) + '\n' )

def workflows_in_use(self):
    """ gathers all the available workflow chains (sequence of workflow ids, ).  """
    in_use = []
    wf_tool = getToolByName(self, 'portal_workflow')
    types_tool = getToolByName(self, 'portal_types')

    in_use.append( wf_tool._default_chain )

    if wf_tool._chains_by_type:
        for chain in wf_tool._chains_by_type.values():
            in_use.append(chain)
    
    return in_use  
 

def getWorklists(self):
    """ instead of manually scraping actions_box, lets:
        query for all worklists in all workflow definitions.
        Returns a dictionary whos value is sequence of dictionaries

        i.e. map[workflow_id]=(workflow definition map, )
        each workflow defintion map contains the following:
        (worklist)id, guard (Guard instance), guard_permissions (permission of Guard instance), 
        catalog_vars (mapping), actbox_name (actions box label), and actbox_url (actions box url)
    """   
    wf_tool=getToolByName(self, 'portal_workflow')
    wf_with_wlists = {}    
    for id in [workflow for seq in workflows_in_use(self) for workflow in seq]:
        # the above list incomprehension merely _flattens_ nested sequences into 1 sequence

        wf=wf_tool.getWorkflowById(id)
        if hasattr(wf, 'worklists'):
            wlists = []
            for worklist in wf.worklists._objects:
                wlist_def=wf.worklists._mapping[worklist['id']]  
                a_wlist = { 'id':worklist['id']
                          , 'guard' : wlist_def.getGuard()
                          , 'guard_permissions' : wlist_def.getGuard().getPermissionsText()
                          , 'catalog_vars' : wlist_def.var_matches
                          , 'name' : getattr(wlist_def, 'actbox_name', None)
                          , 'url' : getattr(wlist_def, 'actbox_url', None) }
                wlists.append(a_wlist)
            # yes, we can duplicates, we filter duplicates out on the client end
            wf_with_wlists[id]=wlists 

    return wf_with_wlists

def testGettingWorklists(self):
    """ careful with this.. it can hose the ZODB """
    wf_tool=getToolByName(self, 'portal_workflow')
    if not hasattr(wf_tool, 'getWorklists'):
        wf_tool.getWorklists = getWorklists
        log('wf_tool doenst have Worklists!')
    else:
        del(wf_tool.getWorklists)
        
        log('wf_tool has getWorklists!')

    for wflow_id, wlist_seq in wf_tool.getWorklists(self).items():
        for wlist in wlist_seq:
            log(wlist)
            permission=wlist['guard'].getPermissionsText()
            log ('permission for ' + wlist['id'] + ' is ' + permission)

    
