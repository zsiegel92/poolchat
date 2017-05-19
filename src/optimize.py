
def optimize_Group(sender_id):
    #TODO:
    #Create a "solution" model in models.py
    #TODO:
    #When calling this function:
#    job = q.enqueue_call(
#    func=optimize_Group, args=(sender_id,), result_ttl=5000
#    )
#    print(job.get_id()) #pass this around as job_id
#
    #TODO: When getting solution:
    #job = Job.fetch(job_id,connection=conn)
#    if job.is_finished:
#        return str(job.result), 200 #job.result may use a result model? And it may use a __repr__ method of the model class in models.py
#    else:
#        return "Nay!", 202
#

#   TODO: This function should write to the "solutions" table of database:
#    solution = Solution(parameters_for_solution_entry)
#    db.session.add(soultion)
#    db.session.commit()
#    return solution.id #solution has an id once it is added to the db!!
    solution = {}
#    return 1
#    TODO: send user who called this function (cf param sender_id) a button to "see optimal solution". Possibly along with a Google Maps link?
    messenger.say(sender_id,"Your group has been optimized! Ask me about it.")
    return "Solution committed"

