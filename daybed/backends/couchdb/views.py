from couchdb.design import ViewDefinition

# Definition of CouchDB design documents, a.k.a. permanent views.


""" Model definitions, by model id."""
model_definitions = ViewDefinition('definitions', 'all', """
function(doc) {
  if (doc.type == "definition") {
    emit(doc._id, doc);
  }
}""")


"""models by policy_id"""
policy_definitions = ViewDefinition('definitions_policy', 'by_policy_id', """
function(doc) {
  if (doc.type == "definition") {
    emit(doc.policy_id, doc);
  }
}
""")

""" Model records, by model name."""
records = ViewDefinition('records', 'by_model', """
function(doc) {
  if (doc.type == "data") {
    emit(doc.model_id, doc);
  }
}""")

""" Record, by id."""
records_all = ViewDefinition('records_all', 'all', """
function(doc) {
  if (doc.type == "data") {
    emit(doc._id, doc);
  }
}""")

"""The groups for an user"""
user_groups = ViewDefinition('groups', 'by_user', """
function(user){
  if(user.type == 'user'){
    for(var i=0; i <= user.groups.length; i++){
      emit(user.name, user.groups[i]);
    }
  }
}
""")

"""The usernames of the users"""
users = ViewDefinition('users', 'by_name', """
function(doc){
  if(doc.type == 'user'){
      emit(doc.name, doc);
  }
}
""")

"""policies by name"""
policies = ViewDefinition('policies', 'by_name', """
function(doc) {
  if (doc.type == "policy") {
    emit(doc.name, doc);
  }
}
""")


l = locals().values()
docs = [v for v in l if isinstance(v, ViewDefinition)]
