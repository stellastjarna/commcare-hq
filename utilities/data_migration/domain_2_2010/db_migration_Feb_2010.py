# The following script performs a database-level migration from
# an old server (pre 2/2010) to a new server (post 2/2010).

# This script assumes it is running off an exact copy of the 
# OLD database, e.g. if a mysqldumb was run and used to create
# this database exactly.
#
# The primary change here is the turnkey integration done by ross
# which includes moving domains into their own app, getting rid of
# the ExtUser class, and doing email based domain registration and
# allowing users to belong to more than one domain. 

from django.db import connection
from django.core.management.commands.syncdb import Command

def run():
    # this script is still very much a work in progress
    print "starting update"
    
    # syncdb creates the domain, user registration, and granular permissions 
    # tables
    _syncdb()
    
    cursor = connection.cursor()
    
    # we need to carry the domains forward.  we'll just use straight up sql, which 
    # allows us to preserve ids for minimal data migration
    
    try:
        cursor.execute("INSERT INTO domain_domain (SELECT id, name, true as is_active FROM hq_domain);")
    except Exception, e:
        print "Problem creating domains!  Your error is %s" % e
        
    # The users will be migrated in place, but they need the domains brought 
    # over from the extuser table.
    cursor.execute("SELECT user_ptr_id, domain_id FROM hq_extuser")
    rows = cursor.fetchall()
    
    from domain.models import Domain, Membership
    from django.contrib.auth.models import User
    from django.contrib.contenttypes.models import ContentType
    
    
    for user_id, domain_id in rows:
        domain = Domain.objects.get(id=domain_id)
        # create the new domain associations with the Membership objects
        ct = ContentType.objects.get_for_model(User)
        mem = Membership(domain=domain, member_type=ct, is_active=True, member_id=user_id)
        mem.save()        
    
    
    print "finished update"

def _syncdb():
    print "syncdb"
    sync = Command()
    sync.handle()
    print "done syncdb"    